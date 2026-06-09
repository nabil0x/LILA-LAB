"""
Batch annotation tool for BENI 300-article set.

Usage:
    # Extract a batch for annotation
    python3 annotate_batch.py extract --start 0 --end 20

    # Save annotations after I provide them
    python3 annotate_batch.py save --start 0 --end 20 --annotations '[
        {"id": "bnlp_train_xxx", "economic_relevance": "Not Economic", ...},
        ...
    ]'

    # Show annotation progress
    python3 annotate_batch.py status
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BATCH_PATH = Path(__file__).parent / "exports" / "beni_300_batch.json"
OUTPUT_DIR = Path(__file__).parent / "exports" / "llm_annotations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_articles() -> list[dict[str, Any]]:
    return json.loads(BATCH_PATH.read_text(encoding="utf-8"))


def cmd_extract(start: int, end: int):
    articles = load_articles()
    batch = articles[start:end]
    print(f"=== BENI Annotation Batch {start}-{end-1} ({len(batch)} articles) ===\n")
    for i, a in enumerate(batch):
        text = a["data"]["text"]
        topic = a["data"]["topic"]
        kw = a["data"]["keyword_label"]
        print(f"[{start+i}] ID: {a['id']}")
        print(f"    Topic: {topic} | Keyword: {kw}")
        print(f"    Text ({len(text)} chars):")
        print(f"    {text[:500]}")
        if len(text) > 500:
            print(f"    [...truncated, {len(text)-500} more chars]")
        print()


def cmd_save(start: int, end: int, annotations_json: str):
    """Save annotations from my JSON response."""
    annotations = json.loads(annotations_json)
    output_path = OUTPUT_DIR / f"batch_{start:03d}_{end-1:03d}.json"
    output_path.write_text(
        json.dumps(annotations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(annotations)} annotations -> {output_path}")


def cmd_status():
    """Show annotation completion status."""
    existing = sorted(OUTPUT_DIR.glob("batch_*.json"))
    completed_ids = set()
    for f in existing:
        data = json.loads(f.read_text(encoding="utf-8"))
        for item in data:
            if "economic_relevance" in item:
                completed_ids.add(item.get("id", ""))
    total = len(load_articles())
    print(f"Annotated: {len(completed_ids)} / {total}")
    remaining = total - len(completed_ids)
    if remaining > 0:
        articles = load_articles()
        for a in articles:
            if a["id"] not in completed_ids:
                print(f"  Next: {a['id']} (topic={a['data']['topic']})")
                break


def cmd_compile():
    """Compile all batch annotations into a single file."""
    existing = sorted(OUTPUT_DIR.glob("batch_*.json"))
    all_annotations = {}
    for f in existing:
        data = json.loads(f.read_text(encoding="utf-8"))
        for item in data:
            all_annotations[item["id"]] = item

    articles = load_articles()
    output = []
    for a in articles:
        ann = all_annotations.get(a["id"], {})
        entry = {
            "id": a["id"],
            "data": a["data"],
            "llm_annotation": {
                "provider": "claude",
                "model": "claude-sonnet-4-20250514",
                **ann,
            },
        }
        output.append(entry)

    output_path = OUTPUT_DIR.parent / "llm_annotated_full.json"
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Compiled {len(output)} annotations -> {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    p_extract = sub.add_parser("extract")
    p_extract.add_argument("--start", type=int, required=True)
    p_extract.add_argument("--end", type=int, required=True)

    p_save = sub.add_parser("save")
    p_save.add_argument("--start", type=int, required=True)
    p_save.add_argument("--end", type=int, required=True)
    p_save.add_argument("--annotations", type=str, required=True)

    sub.add_parser("status")
    sub.add_parser("compile")

    args = parser.parse_args()

    if args.command == "extract":
        cmd_extract(args.start, args.end)
    elif args.command == "save":
        cmd_save(args.start, args.end, args.annotations)
    elif args.command == "status":
        cmd_status()
    elif args.command == "compile":
        cmd_compile()
    else:
        parser.print_help()
