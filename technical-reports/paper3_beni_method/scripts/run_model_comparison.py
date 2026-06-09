"""
Three-model comparison: TF-IDF vs BanglaBERT vs LLM vs Gold Standard.

Computes:
  - Per-model accuracy, precision, recall, F1, Cohen's κ against gold standard
  - Pairwise McNemar's test for statistically significant disagreement patterns
  - 3-way confusion tensor (gold × model1 × model2)
  - Per-error breakdown (where each model gets it wrong)

Usage:
    python3 run_model_comparison.py

Output:
    exports/model_comparison.json   — Full report
    exports/model_comparison.txt    — Human-readable summary
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2

EXPORTS_DIR = Path(__file__).parent / "exports"
BATCH_WITH_ML = EXPORTS_DIR / "beni_300_batch_with_ml.json"
GOLD_STANDARD = EXPORTS_DIR / "gold_standard.json"
LLM_ANNOTATED = EXPORTS_DIR / "llm_annotated_full.json"

Economic = "Economic"
NotEconomic = "Not Economic"
LABELS = [Economic, NotEconomic]
MODEL_NAMES = {
    "tfidf_potrika_timeseries": "TF-IDF",
    "banglabert_bnwp_prelabel": "BanglaBERT",
}


def cohens_kappa(y1: list[str], y2: list[str]) -> float:
    n = len(y1)
    if n == 0:
        return 0.0
    labels = sorted(set(y1) | set(y2))
    n_classes = len(labels)
    cm = np.zeros((n_classes, n_classes), dtype=int)
    idx = {l: i for i, l in enumerate(labels)}
    for a, b in zip(y1, y2):
        cm[idx[a], idx[b]] += 1
    p_o = np.trace(cm) / n
    row_sums = cm.sum(axis=1)
    col_sums = cm.sum(axis=0)
    p_e = sum(row_sums[i] * col_sums[i] for i in range(n_classes)) / (n * n)
    if p_e == 1:
        return 0.0
    return (p_o - p_e) / (1 - p_e)


def mcnemar_test(y_model_a: list[str], y_model_b: list[str], y_gold: list[str]) -> dict[str, Any]:
    """
    McNemar's test for matched-pair binary classification.

    Tests H0: the two models have equal error rates.
    Counts discordant pairs where one model is correct and the other is wrong.
    """
    n_01 = 0  # A wrong, B right
    n_10 = 0  # A right, B wrong
    for ga, gb, gold in zip(y_model_a, y_model_b, y_gold):
        a_wrong = ga != gold
        b_wrong = gb != gold
        if a_wrong and not b_wrong:
            n_01 += 1
        elif not a_wrong and b_wrong:
            n_10 += 1

    total_discordant = n_01 + n_10
    if total_discordant == 0:
        chi2_stat = 0.0
        p_value = 1.0
    else:
        chi2_stat = ((n_01 - n_10) ** 2) / total_discordant
        p_value = 1.0 - chi2.cdf(chi2_stat, df=1)

    return {
        "n_A_wrong_B_right": n_01,
        "n_A_right_B_wrong": n_10,
        "n_discordant_pairs": total_discordant,
        "chi_squared": round(chi2_stat, 4),
        "p_value": round(p_value, 6),
        "significant_at_005": bool(p_value < 0.05),
    }


def classification_metrics(y_pred: list[str], y_true: list[str]) -> dict[str, Any]:
    n = len(y_pred)
    correct = sum(1 for p, t in zip(y_pred, y_true) if p == t)
    accuracy = correct / n if n > 0 else 0.0
    kappa = cohens_kappa(y_pred, y_true)

    tp = sum(1 for p, t in zip(y_pred, y_true) if p == Economic and t == Economic)
    fp = sum(1 for p, t in zip(y_pred, y_true) if p == Economic and t == NotEconomic)
    fn = sum(1 for p, t in zip(y_pred, y_true) if p == NotEconomic and t == Economic)
    tn = sum(1 for p, t in zip(y_pred, y_true) if p == NotEconomic and t == NotEconomic)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    conf_matrix = {
        Economic: {Economic: tp, NotEconomic: fp},
        NotEconomic: {Economic: fn, NotEconomic: tn},
    }

    return {
        "n": n,
        "n_economic_predicted": sum(1 for p in y_pred if p == Economic),
        "n_economic_true": sum(1 for t in y_true if t == Economic),
        "accuracy": round(accuracy, 4),
        "cohens_kappa": round(kappa, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "confusion_matrix": conf_matrix,
    }


def load_gold(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for item in data:
        aid = item.get("id", "")
        label = item.get("economic_relevance", "")
        result[aid] = label
    return result


def load_llm(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for item in data:
        aid = item.get("id", "")
        ann = item.get("llm_annotation", {})
        label = ann.get("economic_relevance")
        if label in (Economic, NotEconomic):
            result[aid] = label
    return result


def load_ml_predictions(path: Path) -> dict[str, dict[str, str]]:
    """Returns {article_id: {model_version: label}}."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, str]] = {}
    for item in data:
        aid = item.get("id") or item.get("data", {}).get("id", "")
        for pred in item.get("predictions", []):
            mv = pred.get("model_version", "")
            for r in pred.get("result", []):
                if r.get("from_name") == "economic_relevance":
                    label = r["value"]["choices"][0]
                    result.setdefault(aid, {})[mv] = label
    return result


def agreement_between(
    y_a: list[str], y_b: list[str], label_a: str, label_b: str
) -> dict[str, Any]:
    """Compute agreement metrics between two sets of labels."""
    n = len(y_a)
    agree = sum(1 for a, b in zip(y_a, y_b) if a == b)
    return {
        "n": n,
        "n_agree": agree,
        "observed_agreement": round(agree / n, 4),
        "cohens_kappa": round(cohens_kappa(y_a, y_b), 4),
        "label_a": label_a,
        "label_b": label_b,
    }


def error_analysis(
    article_ids: list[str],
    y_pred: list[str],
    y_gold: list[str],
    model_name: str,
) -> dict[str, list[dict[str, Any]]]:
    """Categorise errors by type (false positive, false negative)."""
    fp, fn = [], []
    for aid, pred, gold in zip(article_ids, y_pred, y_gold):
        if pred == Economic and gold == NotEconomic:
            fp.append({"id": aid, "model": model_name})
        elif pred == NotEconomic and gold == Economic:
            fn.append({"id": aid, "model": model_name})
    return {"false_positives": fp, "false_negatives": fn}


def main():
    print("=" * 60)
    print("  Three-Model Comparison: TF-IDF vs BanglaBERT vs LLM")
    print("=" * 60)

    # ── Load all data sources ──────────────────────────────────────────
    gold = load_gold(GOLD_STANDARD)
    print(f"\nGold standard: {len(gold)} articles ({sum(1 for v in gold.values() if v == Economic)} Economic)")

    llm = load_llm(LLM_ANNOTATED)
    print(f"LLM annotations: {len(llm)} articles ({sum(1 for v in llm.values() if v == Economic)} Economic)")

    ml = load_ml_predictions(BATCH_WITH_ML)
    print(f"ML predictions: {len(ml)} articles")

    tfidf_count = sum(1 for v in ml.values() if "tfidf_potrika_timeseries" in v)
    bangla_count = sum(1 for v in ml.values() if "banglabert_bnwp_prelabel" in v)
    print(f"  TF-IDF: {tfidf_count} articles ({sum(1 for v in ml.values() if v.get('tfidf_potrika_timeseries') == Economic)} Economic)")
    print(f"  BanglaBERT: {bangla_count} articles ({sum(1 for v in ml.values() if v.get('banglabert_bnwp_prelabel') == Economic)} Economic)")

    # ── Build aligned dataset ─────────────────────────────────────────
    common_ids = sorted(set(gold.keys()) & set(llm.keys()) & set(ml.keys()))
    print(f"\nAligned articles (all 4 sources): {len(common_ids)}")

    y_gold: list[str] = []
    y_llm: list[str] = []
    y_tfidf: list[str] = []
    y_bangla: list[str] = []
    for aid in common_ids:
        y_gold.append(gold[aid])
        y_llm.append(llm[aid])
        preds = ml[aid]
        y_tfidf.append(preds.get("tfidf_potrika_timeseries", ""))
        y_bangla.append(preds.get("banglabert_bnwp_prelabel", ""))

    # Filter to articles where all labels are valid
    valid = [
        i
        for i in range(len(common_ids))
        if all(x in (Economic, NotEconomic) for x in [y_gold[i], y_llm[i], y_tfidf[i], y_bangla[i]])
    ]
    common_ids = [common_ids[i] for i in valid]
    y_gold = [y_gold[i] for i in valid]
    y_llm = [y_llm[i] for i in valid]
    y_tfidf = [y_tfidf[i] for i in valid]
    y_bangla = [y_bangla[i] for i in valid]
    print(f"Valid aligned articles: {len(common_ids)}")

    # ── Per-model metrics (vs gold standard) ──────────────────────────
    models = {
        "LLM (GPT-4o)": y_llm,
        "TF-IDF + LogReg": y_tfidf,
        "BanglaBERT": y_bangla,
    }
    per_model: dict[str, Any] = {}
    for name, y_pred in models.items():
        m = classification_metrics(y_pred, y_gold)
        err = error_analysis(common_ids, y_pred, y_gold, name)
        per_model[name] = {**m, **err}
        print(f"\n  ── {name} ──")
        print(f"    Accuracy:  {m['accuracy']:.2%}  ({m['n_economic_predicted']} Econ / {m['n']} total)")
        print(f"    κ:         {m['cohens_kappa']:.4f}")
        print(f"    Precision: {m['precision']:.2%}")
        print(f"    Recall:    {m['recall']:.2%}")
        print(f"    F1:        {m['f1']:.2%}")
        print(f"    FP:        {len(err['false_positives'])}  FN: {len(err['false_negatives'])}")

    # ── Pairwise McNemar's tests ──────────────────────────────────────
    model_pairs = [
        ("TF-IDF + LogReg", y_tfidf, "BanglaBERT", y_bangla),
        ("TF-IDF + LogReg", y_tfidf, "LLM (GPT-4o)", y_llm),
        ("BanglaBERT", y_bangla, "LLM (GPT-4o)", y_llm),
    ]
    mcnemar_results: list[dict[str, Any]] = []
    print(f"\n  ── McNemar's Test (H₀: equal error rates) ──")
    for name_a, y_a, name_b, y_b in model_pairs:
        m = mcnemar_test(y_a, y_b, y_gold)
        m["model_A"] = name_a
        m["model_B"] = name_b
        mcnemar_results.append(m)
        sig = " *** p<0.05" if m["significant_at_005"] else ""
        print(f"    {name_a:22s} vs {name_b:22s}:  χ²={m['chi_squared']:.3f}  p={m['p_value']:.4f}{sig}")
        print(f"      A wrong, B right: {m['n_A_wrong_B_right']:3d}  |  A right, B wrong: {m['n_A_right_B_wrong']:3d}")

    # ── Pairwise agreement (inter-model, not vs gold) ─────────────────
    pairwise = [
        agreement_between(y_tfidf, y_bangla, "TF-IDF", "BanglaBERT"),
        agreement_between(y_tfidf, y_llm, "TF-IDF", "LLM"),
        agreement_between(y_bangla, y_llm, "BanglaBERT", "LLM"),
    ]
    print(f"\n  ── Pairwise Agreement (model vs model) ──")
    for p in pairwise:
        print(f"    {p['label_a']:22s} vs {p['label_b']:22s}:  agree={p['n_agree']:3d}/{p['n']:3d}  "
              f"({p['observed_agreement']:.2%})  κ={p['cohens_kappa']:.4f}")

    # ── 3-way confusion tensor ────────────────────────────────────────
    # 2×2×2: Gold × TF-IDF × BanglaBERT (for articles where LLM == Gold)
    tensor_rows: list[dict[str, Any]] = []
    for aid, g, ll, tf, bl in zip(common_ids, y_gold, y_llm, y_tfidf, y_bangla):
        tensor_rows.append({
            "id": aid,
            "gold": g,
            "llm": ll,
            "tfidf": tf,
            "banglabert": bl,
        })

    # Count patterns
    pattern_counts: dict[str, int] = Counter()
    for r in tensor_rows:
        key = f"G={r['gold'][0]}/L={r['llm'][0]}/T={r['tfidf'][0]}/B={r['banglabert'][0]}"
        pattern_counts[key] += 1

    print(f"\n  ── 4-Way Pattern Summary (Gold / LLM / TF-IDF / BanglaBERT) ──")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"    {pattern:32s}  n={count:3d}")

    # ── Where each model disagrees with gold ──────────────────────────
    all_errors: list[dict[str, Any]] = []
    for aid, g, ll, tf, bl in zip(common_ids, y_gold, y_llm, y_tfidf, y_bangla):
        if g != ll or g != tf or g != bl:
            row = {"id": aid, "gold": g, "llm": ll, "tfidf": tf, "banglabert": bl}
            row["models_wrong"] = [m for m, v in [("LLM", ll), ("TF-IDF", tf), ("BanglaBERT", bl)] if v != g]
            all_errors.append(row)
    print(f"\n  ── Error Log (articles where at least one model disagrees with gold) ──")
    print(f"    Total error articles: {len(all_errors)} / {len(common_ids)}")
    for err in all_errors:
        print(f"    {err['id']:22s}  gold={err['gold'][0]:1s}  llm={err['llm'][0]:1s}  "
              f"tfidf={err['tfidf'][0]:1s}  bert={err['banglabert'][0]:1s}  "
              f"wrong: {','.join(err['models_wrong']):20s}")

    # ── Model ranking (primary metric: F1) ────────────────────────────
    ranking = sorted(per_model.items(), key=lambda x: x[1]["f1"], reverse=True)
    print(f"\n  ── Model Ranking (by F1 vs Gold Standard) ──")
    for rank, (name, m) in enumerate(ranking, 1):
        print(f"    {rank}. {name:22s}  F1={m['f1']:.2%}  Acc={m['accuracy']:.2%}  κ={m['cohens_kappa']:.4f}")

    # ── Assemble report ───────────────────────────────────────────────
    report = {
        "metadata": {
            "n_total": len(common_ids),
            "n_economic_gold": sum(1 for v in y_gold if v == Economic),
            "n_economic_llm": sum(1 for v in y_llm if v == Economic),
            "n_economic_tfidf": sum(1 for v in y_tfidf if v == Economic),
            "n_economic_banglabert": sum(1 for v in y_bangla if v == Economic),
        },
        "per_model_vs_gold": per_model,
        "pairwise_mcnemar": mcnemar_results,
        "pairwise_agreement": pairwise,
        "pattern_summary": dict(pattern_counts.most_common()),
        "error_log": all_errors,
        "ranking": [{"rank": i, "model": name, **m} for i, (name, m) in enumerate(ranking, 1)],
    }

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EXPORTS_DIR / "model_comparison.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Report saved -> {json_path}")

    # ── Text summary ───────────────────────────────────────────────────
    lines = [
        "=" * 62,
        "  3-MODEL COMPARISON: TF-IDF vs BanglaBERT vs LLM (vs Gold Standard)",
        "=" * 62,
        "",
        f"Dataset: {len(common_ids)} aligned articles",
        f"  Gold Economic:     {report['metadata']['n_economic_gold']}",
        f"  LLM Economic:      {report['metadata']['n_economic_llm']}",
        f"  TF-IDF Economic:   {report['metadata']['n_economic_tfidf']}",
        f"  BanglaBERT Economic: {report['metadata']['n_economic_banglabert']}",
        "",
        "── Per-Model Performance (vs Gold Standard) ──",
        f"  {'Model':22s} {'Acc':>6s} {'κ':>6s} {'Prec':>6s} {'Recall':>6s} {'F1':>6s} {'Econ':>5s} {'FP':>4s} {'FN':>4s}",
        "  " + "-" * 68,
    ]
    for name, m in ranking:
        lines.append(
            f"  {name:22s} {m['accuracy']:.2%} {m['cohens_kappa']:.4f} {m['precision']:.2%} "
            f"{m['recall']:.2%} {m['f1']:.2%} {m['n_economic_predicted']:3d}/{m['n']:3d} "
            f"{len(m['false_positives']):3d} {len(m['false_negatives']):3d}"
        )

    lines += [
        "",
        "── Pairwise McNemar's Test (H₀: equal error rates) ──",
        f"  {'Model A':22s} vs {'Model B':22s}  {'χ²':>6s} {'p-value':>8s} {'Sig(0.05)':>10s}  Discordant",
        "  " + "-" * 72,
    ]
    for m in mcnemar_results:
        lines.append(
            f"  {m['model_A']:22s} vs {m['model_B']:22s}  {m['chi_squared']:>6.3f} {m['p_value']:>8.4f} "
            f"{'Yes' if m['significant_at_005'] else 'No':>10s}  "
            f"{m['n_A_wrong_B_right']}+{m['n_A_right_B_wrong']}={m['n_discordant_pairs']}"
        )

    lines += [
        "",
        "── Pairwise Inter-Model Agreement (no gold) ──",
        f"  {'Model A':22s} vs {'Model B':22s}  {'Agree':>8s} {'κ':>6s}",
        "  " + "-" * 40,
    ]
    for p in pairwise:
        lines.append(
            f"  {p['label_a']:22s} vs {p['label_b']:22s}  {p['n_agree']:3d}/{p['n']:3d} "
            f"({p['observed_agreement']:.2%})  κ={p['cohens_kappa']:.4f}"
        )

    lines += [
        "",
        "── Pattern Summary (Gold/LLM/TF-IDF/BanglaBERT) ──",
    ]
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {pattern:36s}  n={count:3d}")

    lines += [
        "",
        "── Error Detail ──",
        f"  Articles with ≥1 model wrong: {len(all_errors)} / {len(common_ids)}",
    ]
    for err in all_errors:
        lines.append(
            f"  {err['id']:22s}  gold={err['gold'][0]:1s}  llm={err['llm'][0]:1s}  "
            f"tfidf={err['tfidf'][0]:1s}  bert={err['banglabert'][0]:1s}  "
            f"wrong: {','.join(err['models_wrong'])}"
        )

    lines += [
        "",
        "─" * 62,
    ]
    txt_content = "\n".join(lines)
    txt_path = EXPORTS_DIR / "model_comparison.txt"
    txt_path.write_text(txt_content, encoding="utf-8")
    print(f"  Summary saved -> {txt_path}")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
