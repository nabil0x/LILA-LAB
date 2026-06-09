from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any


ECONOMIC_CATEGORIES = {
    "অর্থনীতি",
    "ব্যবসা",
    "বাণিজ্য",
    "শিল্প-বাণিজ্য",
    "শিল্প ও বাণিজ্য",
    "কর্পোরেট",
}

STRONG_ECONOMIC_TERMS = {
    "অর্থনীতি",
    "অর্থনৈতিক",
    "মূল্যস্ফীতি",
    "মুদ্রাস্ফীতি",
    "দ্রব্যমূল্য",
    "বাজারদর",
    "ডলার",
    "রিজার্ভ",
    "বাংলাদেশ ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "বিনিময় হার",
    "বিনিময় হার",
    "সুদের হার",
    "ব্যাংক",
    "ঋণ",
    "আমানত",
    "তারল্য",
    "বাজেট",
    "কর",
    "ভ্যাট",
    "শুল্ক",
    "রাজস্ব",
    "ভর্তুকি",
    "ঘাটতি",
    "রপ্তানি",
    "আমদানি",
    "এলসি",
    "বাণিজ্য",
    "বন্দর",
    "জিডিপি",
    "প্রবৃদ্ধি",
    "বিনিয়োগ",
    "বিনিয়োগ",
    "রেমিট্যান্স",
    "প্রবাসী আয়",
    "প্রবাসী আয়",
    "শেয়ারবাজার",
    "শেয়ারবাজার",
    "পুঁজিবাজার",
    "শ্রমবাজার",
    "কর্মসংস্থান",
    "বেকারত্ব",
    "মজুরি",
    "বেতন",
    "গার্মেন্ট",
    "পোশাকশিল্প",
}

CONTEXT_ECONOMIC_TERMS = {
    "দাম",
    "মূল্য",
    "বাজার",
    "ব্যবসা",
    "ব্যবসায়ী",
    "ব্যবসায়ী",
    "ক্রেতা",
    "ভোক্তা",
    "পণ্য",
    "সরবরাহ",
    "চাহিদা",
    "উৎপাদন",
    "কারখানা",
    "শিল্প",
    "কৃষি",
    "ফসল",
    "চাল",
    "পেঁয়াজ",
    "পেঁয়াজ",
    "তেল",
    "গ্যাস",
    "চাকরি",
    "নিয়োগ",
    "নিয়োগ",
    "কোম্পানি",
    "প্রতিষ্ঠান",
}

NON_ECONOMIC_CATEGORIES = {
    "খেলা",
    "বিনোদন",
    "লাইফস্টাইল",
    "ধর্ম",
    "শিক্ষা",
}


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def category_has(category: str, names: set[str]) -> bool:
    return any(name in category for name in names)


def matched_terms(text: str, terms: set[str]) -> list[str]:
    tokens = set(re.findall(r"[\u0980-\u09FF]+", text))
    matches = []
    for term in terms:
        if " " in term or len(term) > 4:
            if term in text:
                matches.append(term)
        elif term in tokens:
            matches.append(term)
    return sorted(matches)


def source_records(source_dir: Path, max_records: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(source_dir.glob("*.jsonl")):
        for line_no, line in enumerate(path.open(encoding="utf-8"), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = normalize(str(raw.get("Title") or ""))
            content = normalize(str(raw.get("Content") or raw.get("Meta") or ""))
            if len(content) < 120:
                continue
            category = normalize(str(raw.get("Category") or ""))
            source = path.stem
            digest = hashlib.sha1(f"{source}:{line_no}:{title}".encode("utf-8")).hexdigest()[:12]
            text = normalize(f"{title}\n\n{content}")[:5000]
            records.append(
                {
                    "id": f"bangla_news_{source}_{line_no}_{digest}",
                    "source": source,
                    "source_file": path.name,
                    "source_line": line_no,
                    "title": title,
                    "category": category,
                    "time": normalize(str(raw.get("Time") or "")),
                    "text": text,
                }
            )
            if len(records) >= max_records:
                return records
    return records


def score_record(record: dict[str, Any]) -> dict[str, Any]:
    text = normalize(f"{record['title']} {record['category']} {record['text']}")
    strong = matched_terms(text, STRONG_ECONOMIC_TERMS)
    context = matched_terms(text, CONTEXT_ECONOMIC_TERMS)
    category = record["category"]
    category_econ = category_has(category, ECONOMIC_CATEGORIES)
    category_non_econ = category_has(category, NON_ECONOMIC_CATEGORIES)

    score = len(strong) * 2 + len(context)
    if category_econ:
        score += 5
    if category_non_econ:
        score -= 2

    is_economic = category_econ or (len(strong) >= 1 and score >= 3)
    if category_non_econ and not category_econ and len(strong) < 2:
        is_economic = False
    if is_economic:
        label = "Economic"
        confidence = 3 if score >= 6 or category_econ else 2
        difficulty = "Clear-cut" if confidence == 3 else "Borderline"
    else:
        label = "Not Economic"
        confidence = 3 if score <= 0 else 2
        difficulty = None

    return {
        "economic_relevance": label,
        "confidence": confidence,
        "difficulty": difficulty,
        "economic_score": score,
        "matched_strong_terms": strong[:12],
        "matched_context_terms": context[:12],
    }


def stratified_sample(records: list[dict[str, Any]], n: int, econ_ratio: float, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    annotated = [{**record, "annotation": score_record(record)} for record in records]
    econ = [r for r in annotated if r["annotation"]["economic_relevance"] == "Economic"]
    non_econ = [r for r in annotated if r["annotation"]["economic_relevance"] == "Not Economic"]

    n_econ = min(len(econ), round(n * econ_ratio))
    n_non = min(len(non_econ), n - n_econ)
    if n_econ + n_non < n:
        remainder_pool = econ[n_econ:] if len(non_econ) <= n_non else non_econ[n_non:]
        rng.shuffle(remainder_pool)
        extra = remainder_pool[: n - n_econ - n_non]
    else:
        extra = []

    rng.shuffle(econ)
    rng.shuffle(non_econ)
    selected = econ[:n_econ] + non_econ[:n_non] + extra
    rng.shuffle(selected)
    return selected[:n]


def to_jsonl_record(record: dict[str, Any]) -> dict[str, Any]:
    annotation = record["annotation"]
    return {
        "id": record["id"],
        "text": record["text"],
        "title": record["title"],
        "category": record["category"],
        "time": record["time"],
        "source": record["source"],
        "source_file": record["source_file"],
        "source_line": record["source_line"],
        "economic_relevance": annotation["economic_relevance"],
        "confidence": annotation["confidence"],
        "difficulty": annotation["difficulty"],
        "annotation_method": "llm_assisted_bangla_lexicon_v1",
        "requires_human_review": True,
        "economic_score": annotation["economic_score"],
        "matched_strong_terms": annotation["matched_strong_terms"],
        "matched_context_terms": annotation["matched_context_terms"],
    }


def to_labelstudio_task(record: dict[str, Any]) -> dict[str, Any]:
    annotation = record["annotation"]
    result = [
        {
            "from_name": "economic_relevance",
            "to_name": "article_text",
            "type": "choices",
            "value": {"choices": [annotation["economic_relevance"]]},
        },
        {
            "from_name": "confidence",
            "to_name": "article_text",
            "type": "rating",
            "value": {"rating": annotation["confidence"]},
        },
    ]
    if annotation["difficulty"]:
        result.append(
            {
                "from_name": "difficulty",
                "to_name": "article_text",
                "type": "choices",
                "value": {"choices": [annotation["difficulty"]]},
            }
        )
    return {
        "id": record["id"],
        "data": {
            "text": record["text"],
            "topic": record["category"],
            "keyword_label": 1 if annotation["economic_relevance"] == "Economic" else 0,
            "source": record["source"],
        },
        "annotations": [
            {
                "completed_by": "llm_assisted_bangla_lexicon_v1",
                "result": result,
                "was_cancelled": False,
                "ground_truth": False,
            }
        ],
        "meta": {
            "requires_human_review": True,
            "source_file": record["source_file"],
            "source_line": record["source_line"],
            "economic_score": annotation["economic_score"],
            "matched_strong_terms": annotation["matched_strong_terms"],
            "matched_context_terms": annotation["matched_context_terms"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("beni/Bangla_News_Database"))
    parser.add_argument("--output-dir", type=Path, default=Path("beni/annotation/exports"))
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--econ-ratio", type=float, default=0.4)
    parser.add_argument("--seed", type=int, default=20260607)
    parser.add_argument("--max-records", type=int, default=5000)
    args = parser.parse_args()

    records = source_records(args.source_dir, args.max_records)
    selected = stratified_sample(records, args.n, args.econ_ratio, args.seed)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.output_dir / "llm_assisted_300_annotations.jsonl"
    ls_path = args.output_dir / "llm_assisted_300_labelstudio_completed.json"
    summary_path = args.output_dir / "llm_assisted_300_summary.json"

    jsonl_path.write_text(
        "\n".join(json.dumps(to_jsonl_record(record), ensure_ascii=False) for record in selected) + "\n",
        encoding="utf-8",
    )
    ls_path.write_text(
        json.dumps([to_labelstudio_task(record) for record in selected], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    labels: dict[str, int] = {}
    for record in selected:
        label = record["annotation"]["economic_relevance"]
        labels[label] = labels.get(label, 0) + 1
    summary = {
        "n": len(selected),
        "source_dir": str(args.source_dir),
        "annotation_method": "llm_assisted_bangla_lexicon_v1",
        "requires_human_review": True,
        "label_counts": labels,
        "outputs": {
            "jsonl": str(jsonl_path),
            "labelstudio_completed": str(ls_path),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
