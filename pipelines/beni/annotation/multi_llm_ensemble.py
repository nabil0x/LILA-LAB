"""
Multi-LLM Ensemble Pipeline for BENI — Open-Source Local Models.

Uses 3 locally-run open-source LLMs via Ollama:
  - Llama 2 7B    (Meta, Llama family)
  - Qwen 2.5 3B   (Alibaba, Qwen family)
  - Gemma 2 2B    (Google, Gemma family)

No paid API keys required. Runs entirely on local hardware.

Usage:
    # Run all 3 models on the full 300-article batch
    python3 multi_llm_ensemble.py

    # Quick test on 5 articles
    python3 multi_llm_ensemble.py --max-articles 5

    # Resume: skips models that already have output
    python3 multi_llm_ensemble.py

    # Force re-run all models
    python3 multi_llm_ensemble.py --force

Output:
    exports/ensemble_results/
    ├── llama2_7b_results.json           # Per-article Llama 2 labels
    ├── qwen2.5_3b_results.json          # Per-article Qwen 2.5 labels
    ├── gemma2_2b_results.json           # Per-article Gemma 2 labels
    ├── ensemble_consensus.json          # Majority-vote consensus labels
    ├── ensemble_consensus.jsonl          # JSONL format for downstream
    └── ensemble_log.json                # Run metadata + metrics
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

# ── Ensure sibling imports work ─────────────────────────────────────
_HERE = Path(__file__).parent.resolve()
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ── Import shared prompt artifacts ──────────────────────────────────
try:
    from llm_annotate import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
except ImportError as e:
    print(f"[FATAL] Cannot import from llm_annotate.py: {e}")
    sys.exit(1)

# ── Ollama config ───────────────────────────────────────────────────
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434/v1")

MODELS = [
    {
        "name": "llama2",
        "model": "llama2:7b",
        "label": "Llama 2 7B",
        "family": "llama",
        "output_file": "llama2_7b_results.json",
    },
    {
        "name": "qwen2.5",
        "model": "qwen2.5:3b-instruct-q4_K_M",
        "label": "Qwen 2.5 3B",
        "family": "qwen2.5",
        "output_file": "qwen2.5_3b_results.json",
    },
    {
        "name": "gemma2",
        "model": "gemma2:2b",
        "label": "Gemma 2 2B",
        "family": "gemma",
        "output_file": "gemma2_2b_results.json",
    },
]


# ── Ollama API call (via OpenAI-compatible endpoint) ────────────────

def call_ollama(
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int = 600,
) -> str:
    """Call Ollama's OpenAI-compatible chat endpoint."""
    from openai import OpenAI

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return resp.choices[0].message.content


def parse_llm_response(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response (handles markdown fences)."""
    text = text.strip()
    if text.startswith("```"):
        start = text.find("{")
        if start >= 0:
            text = text[start:]
        end = text.rfind("}")
        if end >= 0:
            text = text[: end + 1]
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


# ── Per-model annotation ───────────────────────────────────────────

def annotate_article(
    article: dict[str, Any],
    model_cfg: dict[str, Any],
    seed: int = 42,
) -> dict[str, Any]:
    """Annotate a single article using the specified Ollama model."""
    text = article["data"]["text"][:4000]
    user_msg = USER_PROMPT_TEMPLATE.format(
        article_id=article["id"],
        text=text,
    )
    messages = [{"role": "user", "content": user_msg}]

    for attempt in range(3):
        try:
            raw = call_ollama(model_cfg["model"], SYSTEM_PROMPT, messages)
            result = parse_llm_response(raw)
            return {
                "id": article["id"],
                "data": article["data"],
                "llm_annotation": {
                    "provider": f"ollama/{model_cfg['name']}",
                    "model": model_cfg["model"],
                    "seed": seed,
                    **result,
                },
                "raw_response": raw,
            }
        except json.JSONDecodeError as e:
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": f"ollama/{model_cfg['name']}",
                        "model": model_cfg["model"],
                        "seed": seed,
                        "error": f"JSON parse failed: {e}",
                        "raw": raw if "raw" in dir() else "",
                    },
                }
            time.sleep(1)
        except Exception as e:
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": f"ollama/{model_cfg['name']}",
                        "model": model_cfg["model"],
                        "seed": seed,
                        "error": str(e),
                    },
                }
            time.sleep(2**attempt)


def run_model(
    articles: list[dict[str, Any]],
    model_cfg: dict[str, Any],
    seed: int = 42,
    max_articles: int | None = None,
) -> list[dict[str, Any]]:
    """Run a single Ollama model on all articles. Returns result list in order."""
    label = model_cfg["label"]
    total = max_articles or len(articles)
    indices = list(range(total))

    rng = random.Random(seed)
    rng.shuffle(indices)

    results: list[dict[str, Any]] = [None] * total
    api_calls = 0
    errors = 0

    print(f"\n  ── {label} ({total} articles) ──")

    for pos, idx in enumerate(indices):
        article = articles[idx]
        result = annotate_article(article, model_cfg, seed)
        results[idx] = result
        api_calls += 1

        ann = result.get("llm_annotation", {})
        label_val = ann.get("economic_relevance", "ERROR")
        ok = label_val in ("Economic", "Not Economic")
        if not ok:
            errors += 1
        status = "✓" if ok else "✗"
        conf = ann.get("confidence", "?")
        error = ann.get("error", "")
        if error:
            error_short = error[:60] + "..." if len(error) > 60 else error
            print(f"    [{pos+1:>3d}/{total}] {status} {article['id'][:24]:<24s} → {label_val:<13s}  ⚠ {error_short}")
        else:
            print(f"    [{pos+1:>3d}/{total}] {status} {article['id'][:24]:<24s} → {label_val:<13s} (conf={conf})")

    print(f"  ── {label} complete: {api_calls} calls, {errors} errors ──")
    return results


# ── Consensus building ──────────────────────────────────────────────

def build_consensus(
    per_model: dict[str, list[dict[str, Any]]],
    article_ids: list[str],
) -> dict[str, Any]:
    """Majority-vote consensus across models."""
    n_models = len(per_model)
    model_names = list(per_model.keys())

    by_aid: dict[str, dict[str, Any]] = {}
    for mname, mresults in per_model.items():
        for r in mresults:
            aid = r.get("id", "")
            if aid not in by_aid:
                by_aid[aid] = {}
            by_aid[aid][mname] = r.get("llm_annotation", {})

    consensus_list: list[dict[str, Any]] = []
    pairwise_counts: dict[str, dict[str, int]] = {}
    three_way: Counter = Counter()

    for p1 in model_names:
        pairwise_counts[p1] = {}
        for p2 in model_names:
            pairwise_counts[p1][p2] = {"agree": 0, "disagree": 0, "total": 0}

    for aid in article_ids:
        annotations = by_aid.get(aid, {})

        label_counts: Counter = Counter()
        confidences: dict[str, int] = {}
        for mname in model_names:
            ann = annotations.get(mname, {})
            lbl = ann.get("economic_relevance", "ERROR")
            if lbl in ("Economic", "Not Economic"):
                label_counts[lbl] += 1
            conf = ann.get("confidence")
            confidences[mname] = conf if isinstance(conf, int) else 0

        if not label_counts:
            consensus_label = "ERROR"
            vote_margin = 0
        else:
            most_common = label_counts.most_common()
            consensus_label = most_common[0][0]
            vote_margin = most_common[0][1] - (most_common[1][1] if len(most_common) > 1 else 0)

        agreeing_conf = [
            confidences[m]
            for m in model_names
            if annotations.get(m, {}).get("economic_relevance") == consensus_label
        ]
        consensus_conf = round(sum(agreeing_conf) / len(agreeing_conf), 1) if agreeing_conf else 0

        unique_labels = {annotations.get(m, {}).get("economic_relevance") for m in model_names}
        unique_labels.discard("ERROR")
        unique_labels.discard(None)

        if len(unique_labels) == 1:
            agree_type = "full_agreement"
        elif len(unique_labels) == 2:
            agree_type = "majority"
        elif len(unique_labels) >= 3:
            agree_type = "full_disagreement"
        else:
            agree_type = "insufficient_data"
        three_way[agree_type] += 1

        entry = {
            "id": aid,
            "provider_labels": {
                mname: annotations.get(mname, {}).get("economic_relevance", "ERROR")
                for mname in model_names
            },
            "provider_details": {
                mname: {
                    k: annotations.get(mname, {}).get(k)
                    for k in ["economic_relevance", "confidence", "economic_topic",
                              "sentiment", "narrative_force", "valuation_target", "notes"]
                }
                for mname in model_names
            },
            "ensemble": {
                "economic_relevance": consensus_label,
                "confidence": consensus_conf,
                "vote_margin": vote_margin,
                "vote_distribution": dict(label_counts),
                "agreement_type": agree_type,
            },
        }
        # Copy article data from any available result
        for mname in model_names:
            ann = annotations.get(mname, {})
            if ann.get("economic_relevance"):
                src_data = per_model[mname][0].get("data", {}) if per_model[mname] else {}
                entry["data"] = src_data if src_data else {"topic": "", "keyword_label": 0}
                break
        else:
            entry["data"] = {"topic": "", "keyword_label": 0}

        consensus_list.append(entry)

        # Pairwise counts
        for i, p1 in enumerate(model_names):
            for p2 in model_names[i + 1:]:
                l1 = annotations.get(p1, {}).get("economic_relevance")
                l2 = annotations.get(p2, {}).get("economic_relevance")
                if l1 in ("Economic", "Not Economic") and l2 in ("Economic", "Not Economic"):
                    pairwise_counts[p1][p2]["total"] += 1
                    if l1 == l2:
                        pairwise_counts[p1][p2]["agree"] += 1
                    else:
                        pairwise_counts[p1][p2]["disagree"] += 1

    metrics = {
        "n_articles": len(article_ids),
        "n_models": n_models,
        "model_names": model_names,
        "three_way_agreement": {
            k: {"count": v, "pct": round(v / len(article_ids) * 100, 1) if article_ids else 0}
            for k, v in three_way.items()
        },
        "pairwise_agreement": {},
        "consensus_label_distribution": dict(
            Counter(e["ensemble"]["economic_relevance"] for e in consensus_list)
        ),
    }

    for i, p1 in enumerate(model_names):
        for p2 in model_names[i + 1:]:
            pc = pairwise_counts[p1][p2]
            obs_agree = round(pc["agree"] / pc["total"], 4) if pc["total"] > 0 else 0.0
            metrics["pairwise_agreement"][f"{p1}_vs_{p2}"] = {
                "total": pc["total"],
                "agree": pc["agree"],
                "disagree": pc["disagree"],
                "observed_agreement": obs_agree,
            }

    return {"consensus": consensus_list, "metrics": metrics}


# ── File helpers ────────────────────────────────────────────────────

def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  → Saved to {path.name}")


def save_jsonl(data: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(json.dumps(d, ensure_ascii=False) for d in data) + "\n"
    path.write_text(lines, encoding="utf-8")
    print(f"  → Saved to {path.name}")


# ── CLI ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="BENI Multi-LLM Ensemble — local open-source models via Ollama",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=_HERE / "exports" / "beni_300_batch.json",
        help="Input batch JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_HERE / "exports" / "ensemble_results",
        help="Output directory",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=None,
        help="Limit articles for testing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run models even if output exists",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=[m["name"] for m in MODELS],
        default=None,
        help="Specific models to run (default: all)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BENI Multi-LLM Ensemble — Local Open-Source Models")
    print("=" * 60)

    # ── Check Ollama ────────────────────────────────────────────────
    try:
        from openai import OpenAI
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        available_models = {m.id for m in client.models.list()}
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"  {e}")
        print("  Make sure: 1) Ollama is installed  2) `ollama serve` is running")
        sys.exit(1)

    print(f"\n  Ollama endpoint: {OLLAMA_BASE_URL}")
    print(f"  Models available on server: {len(available_models)}")
    for m in sorted(available_models):
        print(f"    • {m}")

    # ── Select models to run ─────────────────────────────────────────
    selected_models = [
        m for m in MODELS
        if (args.models is None or m["name"] in args.models)
        and m["model"] in available_models
    ]

    if not selected_models:
        print("\n[ERROR] None of the required models are available in Ollama.")
        print("Pull them with:")
        for m in MODELS:
            if m["model"] not in available_models:
                print(f"  ollama pull {m['model']}")
        sys.exit(1)

    if len(selected_models) < 2:
        print(f"\n[WARNING] Only {len(selected_models)} model(s) available. Need ≥2 for ensemble.")

    print(f"\nModels selected ({len(selected_models)}):")
    for m in selected_models:
        print(f"  ✓ {m['label']:>12s}  ({m['model']})")

    # ── Load articles ────────────────────────────────────────────────
    if not args.input.exists():
        print(f"\n[ERROR] Input not found: {args.input}")
        sys.exit(1)

    articles = json.loads(args.input.read_text(encoding="utf-8"))
    if args.max_articles:
        articles = articles[:args.max_articles]
    print(f"\nLoaded {len(articles)} articles from {args.input.name}")

    # ── Run each model ───────────────────────────────────────────────
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    per_model_results: dict[str, list[dict[str, Any]]] = {}
    run_log: dict[str, Any] = {
        "input": str(args.input),
        "n_articles": len(articles),
        "seed": args.seed,
        "ollama_endpoint": OLLAMA_BASE_URL,
        "models_selected": [m["name"] for m in selected_models],
        "models_ran": [],
        "models_skipped": [],
    }

    for cfg in selected_models:
        out_path = output_dir / cfg["output_file"]
        if out_path.exists() and not args.force:
            print(f"\n  → {cfg['label']} results exist (use --force to re-run)")
            results = json.loads(out_path.read_text(encoding="utf-8"))
            per_model_results[cfg["name"]] = results
            run_log["models_skipped"].append(cfg["name"])
            continue

        results = run_model(articles, cfg, seed=args.seed, max_articles=args.max_articles)
        save_json(results, out_path)
        per_model_results[cfg["name"]] = results
        run_log["models_ran"].append(cfg["name"])

    if len(per_model_results) < 2:
        print("\n[ERROR] Need at least 2 model results for consensus. Aborting.")
        sys.exit(1)

    # ── Build consensus ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Building consensus from {len(per_model_results)} models...")
    article_ids = [a["id"] for a in articles]
    ensemble = build_consensus(per_model_results, article_ids)

    # ── Save ─────────────────────────────────────────────────────────
    consensus_path = output_dir / "ensemble_consensus.json"
    consensus_jsonl_path = output_dir / "ensemble_consensus.jsonl"
    log_path = output_dir / "ensemble_log.json"

    save_json(ensemble["consensus"], consensus_path)
    save_jsonl(ensemble["consensus"], consensus_jsonl_path)
    run_log["metrics"] = ensemble["metrics"]
    save_json(run_log, log_path)

    # ── Print summary ────────────────────────────────────────────────
    m = ensemble["metrics"]
    print(f"\n{'='*60}")
    print("Ensemble Summary")
    print(f"{'='*60}")
    print(f"  Articles:          {m['n_articles']}")
    print(f"  Models:            {', '.join(m['model_names'])}")
    print(f"\n  Three-Way Agreement:")
    for k, v in m["three_way_agreement"].items():
        print(f"    {k:<25s}: {v['count']:>4d} ({v['pct']:.1f}%)")
    print(f"\n  Pairwise Agreement (observed):")
    for pair, stats in m["pairwise_agreement"].items():
        print(f"    {pair:<25s}: {stats['observed_agreement']:.2%} ({stats['agree']}/{stats['total']})")
    print(f"\n  Consensus Labels:")
    for label, count in m["consensus_label_distribution"].items():
        pct = count / m["n_articles"] * 100
        print(f"    {label:<25s}: {count:>4d} ({pct:.1f}%)")
    print(f"\n  Output: {output_dir}/")
    for cfg in selected_models:
        print(f"    {cfg['output_file']:<32s}")
    print(f"    ensemble_consensus.json")
    print(f"    ensemble_consensus.jsonl")
    print(f"    ensemble_log.json")

    # ── Run report ──────────────────────────────────────────────────
    report_script = _HERE / "ensemble_report.py"
    if report_script.exists():
        print(f"\nNext: python3 ensemble_report.py")


if __name__ == "__main__":
    main()
