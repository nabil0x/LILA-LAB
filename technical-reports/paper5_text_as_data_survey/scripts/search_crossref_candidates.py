from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from urllib.parse import quote_plus


PAPER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PAPER_ROOT / "data" / "crossref_candidate_papers.csv"

SEARCH_QUERIES = [
    "text as data social science",
    "automated text analysis social science",
    "content analysis social sciences methodology",
    "computational text analysis political science",
    "text as data economics",
    "news sentiment economics text as data",
    "economic policy uncertainty newspaper text",
    "topic models social science",
    "structural topic model social science",
    "machine learning text political science",
    "LIWC psychology text analysis",
    "large language models computational social science",
    "ChatGPT text annotation social science",
    "large language models political science",
    "large language models qualitative analysis social science",
    "multilingual text analysis social science",
]

INCLUDE_TERMS = [
    "text",
    "content analysis",
    "automated text",
    "computational text",
    "topic model",
    "sentiment",
    "language model",
    "large language model",
    "chatgpt",
    "liwc",
    "dictionary",
    "narrative",
    "news",
    "social media",
]

SOCIAL_TERMS = [
    "social",
    "politic",
    "economic",
    "sociolog",
    "psycholog",
    "communication",
    "media",
    "policy",
    "public opinion",
    "survey",
    "finance",
]


def query_crossref(query: str, rows: int) -> dict:
    url = (
        "https://api.crossref.org/works"
        f"?query={quote_plus(query)}"
        f"&rows={rows}"
        "&select=DOI,title,author,issued,published-print,published-online,container-title,type,URL,is-referenced-by-count,abstract"
    )
    result = subprocess.run(["curl", "-L", "-s", url], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def first_year(item: dict) -> int | None:
    for field in ("issued", "published-print", "published-online"):
        parts = item.get(field, {}).get("date-parts")
        if parts and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                continue
    return None


def authors(item: dict) -> str:
    names = []
    for author in item.get("author", [])[:6]:
        given = author.get("given", "")
        family = author.get("family", "")
        name = " ".join(part for part in [given, family] if part).strip()
        if name:
            names.append(name)
    if len(item.get("author", [])) > 6:
        names.append("et al.")
    return "; ".join(names)


def title_text(item: dict) -> str:
    title = item.get("title") or []
    return " ".join(str(part) for part in title).strip()


def container_text(item: dict) -> str:
    container = item.get("container-title") or []
    return " ".join(str(part) for part in container).strip()


def likely_relevant(item: dict) -> bool:
    blob = " ".join(
        [
            title_text(item),
            container_text(item),
            str(item.get("abstract", "")),
        ]
    ).lower()
    return any(term in blob for term in INCLUDE_TERMS) and any(term in blob for term in SOCIAL_TERMS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Crossref for Paper 5 candidate papers")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rows", type=int, default=25)
    args = parser.parse_args()

    candidates: dict[str, dict] = {}
    for query in SEARCH_QUERIES:
        payload = query_crossref(query, args.rows)
        for item in payload.get("message", {}).get("items", []):
            doi = str(item.get("DOI") or "").lower()
            title = title_text(item)
            key = doi or title.lower()
            if not title or not key:
                continue
            if not likely_relevant(item):
                continue
            year = first_year(item)
            candidates[key] = {
                "source_query": query,
                "screening_status": "candidate",
                "include_decision": "",
                "exclusion_reason": "",
                "year": year or "",
                "title": title,
                "authors": authors(item),
                "container": container_text(item),
                "type": item.get("type", ""),
                "doi": doi,
                "url": item.get("URL", ""),
                "citation_count_crossref": item.get("is-referenced-by-count", ""),
                "notes": "",
            }

    rows = sorted(candidates.values(), key=lambda row: (str(row["year"]), row["title"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [
            "source_query",
            "screening_status",
            "include_decision",
            "exclusion_reason",
            "year",
            "title",
            "authors",
            "container",
            "type",
            "doi",
            "url",
            "citation_count_crossref",
            "notes",
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} candidate papers to {args.output}")


if __name__ == "__main__":
    main()
