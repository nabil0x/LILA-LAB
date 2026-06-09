"""
BENI 3-LLM Ensemble — Kaggle T4 GPU.

Uses system torch (T4 sm_75+ supported natively).
Skips broken P100 torch 2.3.1 workaround (cp312 incompatibility).

3 open-source models from HuggingFace (4-bit quantized):
  - NousResearch/Llama-2-7b-chat-hf   (Llama 2 7B Chat)
  - Qwen/Qwen2.5-3B-Instruct         (Qwen 2.5 3B)
  - google/gemma-2-2b-it             (Gemma 2 2B)

Output: ensemble_results.tar.gz in /kaggle/working/
"""

import json
import os
import subprocess
import sys
import tarfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

# ── Config ─────────────────────────────────────────────────────────────
# Auto-detect batch file in /kaggle/input/
import glob as _glob
_BATCH_CANDIDATES = _glob.glob("/kaggle/input/**/beni_300_batch.json", recursive=True)
BATCH_PATH = _BATCH_CANDIDATES[0] if _BATCH_CANDIDATES else "/kaggle/input/datasets/annnasernabil/beni-300-batch/beni_300_batch.json"

OUTPUT_DIR = Path("/kaggle/working/ensemble_results")
OUTPUT_TAR = Path("/kaggle/working/ensemble_results.tar.gz")

MODELS_CONFIG = [
    {
        "name": "llama2",
        "hf_id": "NousResearch/Llama-2-7b-chat-hf",
        "label": "Llama 2 7B",
        "out_file": "llama2_7b_results.json",
    },
    {
        "name": "qwen2.5",
        "hf_id": "Qwen/Qwen2.5-3B-Instruct",
        "label": "Qwen 2.5 3B",
        "out_file": "qwen2.5_3b_results.json",
    },
    {
        "name": "gemma2",
        "hf_id": "google/gemma-2-2b-it",
        "label": "Gemma 2 2B",
        "out_file": "gemma2_2b_results.json",
    },
]

SYSTEM_PROMPT = """You are an expert annotator for economic news content in Bengali. You are building the Bangla Economic Narrative Index (BENI), the first Bengali-language economic sentiment index for Bangladesh. Your task is to classify Bengali news articles across multiple dimensions.

Read each article carefully and respond with a JSON object containing your annotations. Be precise and consistent."""

USER_PROMPT_TEMPLATE = """Annotate the following Bengali news article according to the BENI schema.

ARTICLE ID: {article_id}
ARTICLE TEXT:
{text}

Respond with a JSON object containing exactly these fields:

1. "economic_relevance": Either "Economic" or "Not Economic"
   - Economic = article's PRIMARY subject is Bangladesh's economy: GDP, inflation, trade, fiscal policy, banking, forex, agriculture, industry, prices, employment, remittances, economic policy
   - Not Economic = all other content (politics without economic framing, crime, sports, entertainment, culture, general international news, human interest, mythology, religion)

2. "confidence": Integer 1-3
   - 1 = Guessing, 2 = Fairly sure, 3 = Certain

3. "difficulty": "Clear-cut" or "Borderline" (only if economic_relevance = "Economic")

4. "economic_topic": One of these values (only if economic_relevance = "Economic"):
   "inflation_prices", "exchange_rate_reserves", "monetary_banking", "fiscal_budget",
   "trade_external", "employment_wages", "agriculture_food", "industry_investment",
   "remittances", "energy_imports", "general_economy", "other"

5. "sentiment": "negative", "neutral", or "positive" (only if Economic)
   - Rate the ECONOMIC outlook conveyed, not the political tone

6. "narrative_force": One of (only if Economic):
   "crisis_warning", "burden_hardship", "blame_criticism", "reform_solution",
   "stability_confidence", "uncertainty_concern", "resilience_opportunity", "neutral_reporting"

7. "valuation_target": One of (only if Economic):
   "government", "central_bank", "banks_financial", "businesses",
   "households", "global_economy", "market_actors", "unnamed_system"

8. "notes": A brief string explaining your reasoning (optional)

IMPORTANT RULES:
- "কর" (tax) in Bengali is ambiguous — it can mean "tax" (economic) or be a verb suffix / part of compound words (not economic). Read the FULL context to determine which.
- Articles about INDIAN politics (Kolkata, West Bengal) set in India are generally "Not Economic" for BENI since the index targets Bangladesh.
- An article about "rising prices" or "inflation" IS economic even if it mentions politicians.
- An article about a political rally or crime is NOT economic even if it briefly mentions the economy.
- If the article text is truncated, annotate based on what you can see. Note the truncation in "notes".

Respond with ONLY the JSON object, no other text."""


# ── Diagnostics ───────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(msg, flush=True)


# ── Step 1: Verify GPU / Install deps ────────────────────────────────

def verify_gpu() -> None:
    """Verify system torch supports the GPU (T4 sm_75+ expected)."""
    import torch
    log(f"System PyTorch: {torch.__version__}")
    log(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        cap = torch.cuda.get_device_capability(0)
        name = torch.cuda.get_device_name(0)
        log(f"  GPU: {name}  sm_{cap[0]}{cap[1]}  ✓")
    else:
        log("[FATAL] CUDA not available.")
        sys.exit(1)


def install_deps() -> None:
    log("\n=== Installing dependencies ===")
    deps = [
        "transformers>=4.44.0",
        "accelerate>=0.30.0",
        "bitsandbytes>=0.43.0",
        "sentencepiece>=0.2.0",
        "protobuf>=4.25.0",
        "huggingface_hub>=0.24.0",
    ]
    for dep in deps:
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", dep],
            capture_output=True, text=True, timeout=120,
        )
        elapsed = time.time() - t0
        log(f"  dep:{dep} rc={r.returncode} t={elapsed:.0f}s")
        if r.returncode != 0:
            log(f"    stderr: {r.stderr.strip()[-200:]}")
    log("=== Dependencies installed ===\n")


# ── Step 2: Load models & annotate ────────────────────────────────────

def load_model(hf_id: str, device_map: str = "auto"):
    """Load a model in 4-bit for HuggingFace inference."""
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
    )

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    log(f"  Loading tokenizer: {hf_id}")
    tokenizer = AutoTokenizer.from_pretrained(hf_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    log(f"  Loading model: {hf_id} (4-bit)...")
    model = AutoModelForCausalLM.from_pretrained(
        hf_id,
        quantization_config=bnb_config,
        device_map=device_map,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    model.eval()
    log(f"  Model loaded: {hf_id}")
    return tokenizer, model


def annotate_article_hf(
    model,
    tokenizer,
    article: dict[str, Any],
    model_cfg: dict[str, Any],
) -> dict[str, Any]:
    import torch

    text = article["data"]["text"][:2000]
    user_msg = USER_PROMPT_TEMPLATE.format(
        article_id=article["id"],
        text=text,
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    try:
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        prompt = f"{SYSTEM_PROMPT}\n\n{user_msg}"

    model_max = getattr(model.config, "max_position_embeddings", 4096)
    max_input = model_max - 700

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_input).to(
        model.device
    )
    input_len = inputs["input_ids"].shape[1]
    max_new = min(600, model_max - input_len - 10)

    if max_new < 50:
        return {
            "id": article["id"],
            "data": article["data"],
            "llm_annotation": {
                "provider": f"hf/{model_cfg['name']}",
                "model": model_cfg["hf_id"],
                "error": f"Prompt too long: {input_len} tokens (model max {model_max})",
            },
        }

    for attempt in range(3):
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new,
                    temperature=0.0,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            new_tokens = outputs[0][input_len:]
            new_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

            if not new_text:
                log(f"    [WARN] {article['id'][:24]} → empty response ({new_tokens.shape[0]} new tokens, input_len={input_len}, max_new={max_new})")
                raise json.JSONDecodeError("Empty response", "", 0)

            result = parse_llm_response(new_text)
            return {
                "id": article["id"],
                "data": article["data"],
                "llm_annotation": {
                    "provider": f"hf/{model_cfg['name']}",
                    "model": model_cfg["hf_id"],
                    **result,
                },
                "raw_response": new_text,
            }
        except json.JSONDecodeError as e:
            raw_preview = repr(new_text[:200]) if "new_text" in dir() else "N/A"
            log(f"    [WARN] {article['id'][:24]} → JSON parse fail (attempt {attempt+1}/3): raw={raw_preview}")
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": f"hf/{model_cfg['name']}",
                        "model": model_cfg["hf_id"],
                        "error": f"JSON parse failed: {e}",
                        "raw": new_text if "new_text" in dir() else "",
                    },
                }
            time.sleep(1)
        except Exception as e:
            log(f"    [WARN] {article['id'][:24]} → exception (attempt {attempt+1}/3): {e}")
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": f"hf/{model_cfg['name']}",
                        "model": model_cfg["hf_id"],
                        "error": str(e),
                    },
                }
            time.sleep(2**attempt)


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


def run_model(
    articles: list[dict[str, Any]],
    model_cfg: dict[str, Any],
    tokenizer,
    model,
) -> list[dict[str, Any]]:
    """Run a single model on all articles."""
    total = len(articles)
    results: list[dict[str, Any]] = [None] * total
    errors = 0

    label = model_cfg["label"]
    log(f"\n  ── {label} ({total} articles) ──")

    for idx in range(total):
        article = articles[idx]
        result = annotate_article_hf(model, tokenizer, article, model_cfg)
        results[idx] = result

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
            log(f"    [{idx+1:>3d}/{total}] {status} {article['id'][:24]:<24s} → {label_val:<13s}  ⚠ {error_short}")
        else:
            log(f"    [{idx+1:>3d}/{total}] {status} {article['id'][:24]:<24s} → {label_val:<13s} (conf={conf})")

    log(f"  ── {label} complete: {total} articles, {errors} errors ──")
    return results


# ── Step 4: Build consensus ───────────────────────────────────────────

def build_consensus(
    per_model: dict[str, list[dict[str, Any]]],
    article_ids: list[str],
) -> dict[str, Any]:
    """Majority-vote consensus across models."""
    model_names = list(per_model.keys())
    n_models = len(model_names)

    by_aid: dict[str, dict[str, Any]] = {}
    for mname, mresults in per_model.items():
        for r in mresults:
            aid = r.get("id", "")
            if aid not in by_aid:
                by_aid[aid] = {}
            by_aid[aid][mname] = r.get("llm_annotation", {})

    consensus_list: list[dict[str, Any]] = []
    three_way: Counter = Counter()

    pairwise_counts: dict = {}
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
            vote_margin = (
                most_common[0][1] - (most_common[1][1] if len(most_common) > 1 else 0)
            )

        agreeing_conf = [
            confidences[m]
            for m in model_names
            if annotations.get(m, {}).get("economic_relevance") == consensus_label
        ]
        consensus_conf = (
            round(sum(agreeing_conf) / len(agreeing_conf), 1) if agreeing_conf else 0
        )

        unique_labels = {
            annotations.get(m, {}).get("economic_relevance") for m in model_names
        }
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
            "ensemble": {
                "economic_relevance": consensus_label,
                "confidence": consensus_conf,
                "vote_margin": vote_margin,
                "vote_distribution": dict(label_counts),
                "agreement_type": agree_type,
            },
        }
        for mname in model_names:
            ann = annotations.get(mname, {})
            if ann.get("economic_relevance"):
                entry["data"] = per_model[mname][0].get("data", {}) if per_model[mname] else {}
                break
        else:
            entry["data"] = {}

        consensus_list.append(entry)

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


# ── Main ──────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("BENI 3-LLM Ensemble — Kaggle GPU")
    log("=" * 60)

    # 1. Verify GPU (T4 sm_75+ expected)
    verify_gpu()

    # 2. Install dependencies
    install_deps()

    import torch
    log(f"\nUsing PyTorch: {torch.__version__}")
    log(f"GPU: {torch.cuda.get_device_name(0)}")

    # 3. Load articles
    if not os.path.exists(BATCH_PATH):
        log(f"\n[FATAL] Batch not found: {BATCH_PATH}")
        log(f"Contents of /kaggle/input/:")
        for root, dirs, files in os.walk("/kaggle/input/"):
            for f in files:
                log(f"  {os.path.join(root, f)}")
        sys.exit(1)

    with open(BATCH_PATH, encoding="utf-8") as f:
        articles = json.load(f)
    log(f"\nLoaded {len(articles)} articles from {BATCH_PATH}")

    # 5. Check VRAM
    total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    log(f"GPU memory: {total_mem:.1f} GiB")

    # 6. Run each model sequentially
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    per_model_results: dict[str, list[dict]] = {}
    models_succeeded = []
    models_failed = []

    for cfg in MODELS_CONFIG:
        hf_id = cfg["hf_id"]
        label = cfg["label"]
        log(f"\n{'='*60}")
        log(f"Loading {label} ({hf_id})...")
        log(f"{'='*60}")

        try:
            tokenizer, model = load_model(hf_id)
            results = run_model(articles, cfg, tokenizer, model)

            out_path = OUTPUT_DIR / cfg["out_file"]
            out_path.write_text(
                json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            log(f"\n  → Saved {label} results ({len(results)} articles)")

            per_model_results[cfg["name"]] = results
            models_succeeded.append(cfg["name"])

            del model
            del tokenizer
            torch.cuda.empty_cache()

        except Exception as e:
            log(f"\n  ✗ {label} FAILED: {e}")
            models_failed.append(cfg["name"])
            torch.cuda.empty_cache()
            continue

    # 7. Build consensus
    if len(per_model_results) < 2:
        log(f"\n[FATAL] Need ≥2 model results for consensus. Got {len(per_model_results)}.")
        summary = {
            "models_succeeded": models_succeeded,
            "models_failed": models_failed,
            "error": "Insufficient models for consensus",
        }
        (OUTPUT_DIR / "ensemble_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    else:
        log(f"\n{'='*60}")
        log(f"Building consensus from {len(per_model_results)} models...")
        log(f"{'='*60}")

        article_ids = [a["id"] for a in articles]
        ensemble = build_consensus(per_model_results, article_ids)

        (OUTPUT_DIR / "ensemble_consensus.json").write_text(
            json.dumps(ensemble["consensus"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        jsonl_lines = "\n".join(
            json.dumps(d, ensure_ascii=False) for d in ensemble["consensus"]
        ) + "\n"
        (OUTPUT_DIR / "ensemble_consensus.jsonl").write_text(
            jsonl_lines, encoding="utf-8"
        )
        summary = {
            "models_succeeded": models_succeeded,
            "models_failed": models_failed,
            "metrics": ensemble["metrics"],
        }
        (OUTPUT_DIR / "ensemble_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        m = ensemble["metrics"]
        log(f"\n{'='*60}")
        log("Ensemble Summary")
        log(f"{'='*60}")
        log(f"  Articles:          {m['n_articles']}")
        log(f"  Models:            {', '.join(m['model_names'])}")
        log(f"  Three-Way Agreement:")
        for k, v in m["three_way_agreement"].items():
            log(f"    {k:<25s}: {v['count']:>4d} ({v['pct']:.1f}%)")
        log(f"  Consensus Labels:")
        for label, count in m["consensus_label_distribution"].items():
            pct = count / m["n_articles"] * 100
            log(f"    {label:<25s}: {count:>4d} ({pct:.1f}%)")
        log(f"  Pairwise Agreement:")
        for pair, stats in m["pairwise_agreement"].items():
            log(f"    {pair:<25s}: {stats['observed_agreement']:.2%} ({stats['agree']}/{stats['total']})")

    # 8. Create tar.gz
    log(f"\nCreating {OUTPUT_TAR}...")
    with tarfile.open(OUTPUT_TAR, "w:gz") as tar:
        for f in OUTPUT_DIR.iterdir():
            if f.is_file():
                tar.add(f, arcname=f.name)
    log(f"  → Created ({OUTPUT_TAR.stat().st_size / 1024:.0f} KB)")

    log(f"\n{'='*60}")
    log("Done. Download ensemble_results.tar.gz from Kaggle output.")
    log(f"{'='*60}")


if __name__ == "__main__":
    main()
