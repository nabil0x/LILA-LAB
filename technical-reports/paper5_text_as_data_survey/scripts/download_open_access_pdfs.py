from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

import pandas as pd


PAPER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PAPER_ROOT / "data" / "crossref_screening_queue.csv"
DEFAULT_PDF_DIR = PAPER_ROOT / "literature" / "pdfs"
DEFAULT_INVENTORY = PAPER_ROOT / "literature" / "local_pdf_inventory.csv"
DEFAULT_MANIFEST = PAPER_ROOT / "literature" / "open_access_api_download_manifest.csv"


def safe_name(text: str, max_len: int = 120) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len] or "paper"


def run_curl_json(url: str) -> dict | None:
    result = subprocess.run(
        [
            "curl",
            "-L",
            "-s",
            "--max-time",
            "45",
            "-A",
            "BENI Paper 5 OA metadata downloader",
            url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def openalex_pdf_urls(doi: str) -> list[str]:
    if not doi:
        return []
    payload = run_curl_json(f"https://api.openalex.org/works/doi:{quote(doi, safe='')}")
    if not payload:
        return []
    urls = []
    best = payload.get("best_oa_location") or {}
    if best.get("pdf_url"):
        urls.append(best["pdf_url"])
    for loc in payload.get("oa_locations") or []:
        if loc.get("pdf_url"):
            urls.append(loc["pdf_url"])
    return dedupe(urls)


def semantic_scholar_pdf_urls(doi: str) -> list[str]:
    if not doi:
        return []
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/"
        f"DOI:{quote(doi, safe='')}"
        "?fields=title,year,openAccessPdf,url"
    )
    payload = run_curl_json(url)
    if not payload:
        return []
    oa = payload.get("openAccessPdf") or {}
    return [oa["url"]] if oa.get("url") else []


def unpaywall_pdf_urls(doi: str, email: str | None) -> list[str]:
    if not doi or not email:
        return []
    payload = run_curl_json(f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?email={quote(email)}")
    if not payload:
        return []
    urls = []
    best = payload.get("best_oa_location") or {}
    if best.get("url_for_pdf"):
        urls.append(best["url_for_pdf"])
    for loc in payload.get("oa_locations") or []:
        if loc.get("url_for_pdf"):
            urls.append(loc["url_for_pdf"])
    return dedupe(urls)


def arxiv_pdf_urls(doi: str, landing_url: str) -> list[str]:
    blob = " ".join([doi or "", landing_url or ""])
    match = re.search(r"arxiv[.:/](\d{4}\.\d{4,5})(v\d+)?", blob, flags=re.I)
    if match:
        return [f"https://arxiv.org/pdf/{match.group(1)}"]
    return []


def dedupe(urls: list[str]) -> list[str]:
    seen = set()
    out = []
    for url in urls:
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def download_pdf(url: str, path: Path) -> tuple[bool, str]:
    tmp = path.with_suffix(".tmp")
    result = subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "--max-time",
            "90",
            "-A",
            "Mozilla/5.0 BENI Paper 5 OA downloader",
            "-o",
            str(tmp),
            url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        return False, f"curl_failed:{result.returncode}"
    if tmp.read_bytes()[:5] != b"%PDF-" or tmp.stat().st_size < 1024:
        tmp.unlink(missing_ok=True)
        return False, "not_pdf_or_too_small"
    tmp.replace(path)
    return True, "downloaded"


def existing_dois_from_inventory(pdf_dir: Path) -> set[str]:
    dois = set()
    for pdf in pdf_dir.glob("*.pdf"):
        name = pdf.name.lower()
        match = re.search(r"10\.\d{4,9}_[^_]+", name)
        if match:
            dois.add(match.group(0).replace("_", "/", 1).replace("_", "."))
    return dois


def write_inventory(pdf_dir: Path, inventory: Path) -> None:
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    inventory.parent.mkdir(parents=True, exist_ok=True)
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["filename", "size_bytes", "path"])
        writer.writeheader()
        for pdf in pdfs:
            writer.writerow({"filename": pdf.name, "size_bytes": pdf.stat().st_size, "path": str(pdf)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Second-pass open-access PDF downloader via OA APIs")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--unpaywall-email", default=None)
    parser.add_argument("--priority", choices=["all", "screen_first", "screen_second"], default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.35)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.priority != "all" and "screening_priority" in df.columns:
        df = df[df["screening_priority"] == args.priority].copy()
    if args.limit:
        df = df.head(args.limit).copy()

    args.pdf_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    downloaded = 0
    existing_dois = existing_dois_from_inventory(args.pdf_dir)

    for idx, row in df.reset_index(drop=True).iterrows():
        doi = str(row.get("doi", "") or "").strip().lower()
        title = str(row.get("title", "") or "").strip()
        year = str(row.get("year", "") or "").replace(".0", "")
        base = safe_name(f"{year}_{doi.replace('/', '_')}_{title[:60]}")
        local_pdf = args.pdf_dir / f"{base}.pdf"

        status = "skipped_no_oa_pdf"
        api_source = ""
        pdf_url = ""
        message = ""

        if local_pdf.exists() or doi in existing_dois:
            status = "already_exists"
            message = "existing_pdf"
        elif not doi:
            status = "skipped_no_doi"
        else:
            api_urls = [
                ("arxiv", arxiv_pdf_urls(doi, str(row.get("url", "")))),
                ("openalex", openalex_pdf_urls(doi)),
                ("semantic_scholar", semantic_scholar_pdf_urls(doi)),
                ("unpaywall", unpaywall_pdf_urls(doi, args.unpaywall_email)),
            ]
            for source, urls in api_urls:
                for url in urls:
                    api_source = source
                    pdf_url = url
                    ok, message = download_pdf(url, local_pdf)
                    if ok:
                        status = "downloaded"
                        downloaded += 1
                        break
                    status = "failed"
                    time.sleep(args.sleep)
                if status == "downloaded":
                    break
            time.sleep(args.sleep)

        rows.append(
            {
                "row": idx + 1,
                "screening_priority": row.get("screening_priority", ""),
                "year": row.get("year", ""),
                "title": title,
                "authors": row.get("authors", ""),
                "doi": doi,
                "api_source": api_source,
                "pdf_url": pdf_url,
                "download_status": status,
                "message": message,
                "local_pdf": str(local_pdf) if local_pdf.exists() else "",
            }
        )

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    write_inventory(args.pdf_dir, args.inventory)
    counts = pd.Series([row["download_status"] for row in rows]).value_counts().to_dict()
    print(f"Wrote manifest: {args.manifest}")
    print(f"Downloaded new PDFs: {downloaded}")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
