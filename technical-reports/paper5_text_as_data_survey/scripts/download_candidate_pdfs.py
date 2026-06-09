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
DEFAULT_MANIFEST = PAPER_ROOT / "literature" / "download_manifest.csv"


def safe_name(text: str, max_len: int = 120) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len] or "paper"


def curl_json(url: str) -> dict | None:
    result = subprocess.run(
        ["curl", "-L", "-s", "--max-time", "30", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def crossref_pdf_links(doi: str) -> list[str]:
    if not doi:
        return []
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    payload = curl_json(url)
    if not payload:
        return []
    item = payload.get("message", {})
    links = []
    for link in item.get("link", []) or []:
        content_type = str(link.get("content-type", "")).lower()
        link_url = link.get("URL")
        if link_url and ("pdf" in content_type or link_url.lower().endswith(".pdf")):
            links.append(link_url)
    return links


def arxiv_pdf_link(doi: str, url: str) -> str | None:
    blob = " ".join([doi or "", url or ""])
    match = re.search(r"arxiv[.:/](\d{4}\.\d{4,5})(v\d+)?", blob, flags=re.I)
    if match:
        return f"https://arxiv.org/pdf/{match.group(1)}"
    return None


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
            "Mozilla/5.0 BENI literature downloader (academic metadata audit)",
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
    head = tmp.read_bytes()[:5]
    size = tmp.stat().st_size
    if head != b"%PDF-" or size < 1024:
        tmp.unlink(missing_ok=True)
        return False, "not_pdf_or_too_small"
    tmp.replace(path)
    return True, "downloaded"


def candidate_links(row: pd.Series) -> list[str]:
    doi = str(row.get("doi", "") or "").strip()
    url = str(row.get("url", "") or "").strip()
    links = []
    arxiv = arxiv_pdf_link(doi, url)
    if arxiv:
        links.append(arxiv)
    links.extend(crossref_pdf_links(doi))
    seen = set()
    unique = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique.append(link)
    return unique


def main() -> None:
    parser = argparse.ArgumentParser(description="Download legally accessible candidate PDFs")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--priority", choices=["all", "screen_first", "screen_second"], default="all")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.priority != "all" and "screening_priority" in df.columns:
        df = df[df["screening_priority"] == args.priority].copy()

    args.pdf_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, row in df.reset_index(drop=True).iterrows():
        doi = str(row.get("doi", "") or "").strip()
        title = str(row.get("title", "") or "").strip()
        year = str(row.get("year", "") or "").replace(".0", "")
        base = safe_name(f"{year}_{doi.replace('/', '_')}_{title[:60]}")
        pdf_path = args.pdf_dir / f"{base}.pdf"
        status = "skipped_no_pdf_link"
        source_pdf_url = ""
        message = ""

        if pdf_path.exists():
            status = "already_exists"
            message = "existing_pdf"
        else:
            links = candidate_links(row)
            if links:
                for link in links:
                    source_pdf_url = link
                    ok, message = download_pdf(link, pdf_path)
                    if ok:
                        status = "downloaded"
                        break
                    status = "failed"
                    time.sleep(args.sleep)
            time.sleep(args.sleep)

        rows.append(
            {
                "paper_id": i + 1,
                "screening_priority": row.get("screening_priority", ""),
                "year": row.get("year", ""),
                "title": title,
                "authors": row.get("authors", ""),
                "doi": doi,
                "landing_url": row.get("url", ""),
                "source_pdf_url": source_pdf_url,
                "download_status": status,
                "message": message,
                "local_pdf": str(pdf_path) if pdf_path.exists() else "",
            }
        )

    with args.manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    counts = pd.Series([r["download_status"] for r in rows]).value_counts().to_dict()
    print(f"Wrote manifest: {args.manifest}")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
