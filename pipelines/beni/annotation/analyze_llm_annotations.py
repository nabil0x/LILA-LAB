"""
Analyze LLM annotations against TF-IDF baseline and keyword filter.

Computes agreement (Cohen's κ), confusion matrices, per-topic breakdowns,
and base-rate statistics for the 300-article BENI validation set.

Usage:
    python3 analyze_llm_annotations.py
    python3 analyze_llm_annotations.py --self-consistency path/to/second_pass.json

Output:
    exports/analysis_report.json   — Full report with all metrics
    exports/analysis_report.txt    — Human-readable summary
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPORTS_DIR = Path(__file__).parent / "exports"


# ── Agreement Metrics ───────────────────────────────────────────────────

def cohens_kappa(y1: list, y2: list) -> float:
    """Cohen's κ for two raters on a binary/multi-class task."""
    n = len(y1)
    if n == 0:
        return 0.0
    labels = sorted(set(y1) | set(y2))
    po = sum(1 for a, b in zip(y1, y2) if a == b) / n
    c1 = Counter(y1)
    c2 = Counter(y2)
    pe = sum((c1.get(l, 0) / n) * (c2.get(l, 0) / n) for l in labels)
    if abs(pe - 1.0) < 1e-9:
        return 1.0
    return round((po - pe) / (1 - pe), 4)


def confusion_matrix(y_true: list, y_pred: list, labels: list[str]) -> dict[str, dict[str, int]]:
    """Build confusion matrix."""
    cm = {t: {p: 0 for p in labels} for t in labels}
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1
    return cm


def classification_report(y_true: list, y_pred: list, labels: list[str]) -> dict[str, dict[str, float]]:
    """Per-class precision, recall, F1 (treating y_true as reference)."""
    report = {}
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0
        report[label] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
    return report


# ── Data Loaders ─────────────────────────────────────────────────────────

def load_llm_annotations(path: Path) -> dict[str, dict[str, Any]]:
    """Load LLM annotations keyed by article ID."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for item in data:
        aid = item.get("id") or item.get("data", {}).get("id", "")
        ann = item.get("llm_annotation", {})
        result[aid] = {
            "id": aid,
            "economic_relevance": ann.get("economic_relevance"),
            "confidence": ann.get("confidence"),
            "economic_topic": ann.get("economic_topic"),
            "sentiment": ann.get("sentiment"),
            "narrative_force": ann.get("narrative_force"),
            "valuation_target": ann.get("valuation_target"),
            "notes": ann.get("notes", ""),
            "topic": item.get("data", {}).get("topic", ""),
            "keyword_label": item.get("data", {}).get("keyword_label", -1),
        }
    return result


def load_tfidf_predictions(path: Path) -> dict[str, dict[str, Any]]:
    """Load TF-IDF predictions from batch_with_ml, keyed by article ID."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for item in data:
        aid = item.get("id") or item.get("data", {}).get("id", "")
        preds_list = item.get("predictions", [])
        if preds_list:
            pred = preds_list[0]
            for r in pred.get("result", []):
                if r.get("from_name") == "economic_relevance":
                    result[aid] = {
                        "id": aid,
                        "pred_label": r["value"]["choices"][0],
                        "score": pred.get("score", 0.0),
                        "model_version": pred.get("model_version", "unknown"),
                    }
                    break
        # also carry topic and keyword_label
        result[aid].update({
            "topic": item.get("data", {}).get("topic", ""),
            "keyword_label": item.get("data", {}).get("keyword_label", -1),
        })
    return result


def load_gold_standard(path: Path) -> dict[str, dict[str, Any]]:
    """Load gold standard labels keyed by article ID."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {}
    for item in data:
        aid = item.get("id", "")
        result[aid] = item
    return result


def load_second_pass(path: Path) -> dict[str, dict[str, Any]]:
    """Load second-pass annotations for self-consistency."""
    return load_llm_annotations(path)


# ── Analysis Functions ──────────────────────────────────────────────────

def analyze_economic_relevance(
    llm: dict[str, dict[str, Any]],
    tfidf: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compare LLM vs TF-IDF on economic_relevance binary classification."""
    common = sorted(set(llm.keys()) & set(tfidf.keys()))
    y_llm, y_tfidf = [], []
    for aid in common:
        ll = llm[aid].get("economic_relevance", "")
        tt = tfidf[aid].get("pred_label", "")
        if ll and tt:
            y_llm.append(ll)
            y_tfidf.append(tt)

    labels = sorted(set(y_llm) | set(y_tfidf))
    cm = confusion_matrix(y_llm, y_tfidf, labels)
    kappa = cohens_kappa(y_llm, y_tfidf)
    obs_agree = sum(1 for a, b in zip(y_llm, y_tfidf) if a == b) / len(y_llm)
    cr = classification_report(y_llm, y_tfidf, labels)

    # Agreement by topic
    topic_agree: dict[str, dict[str, Any]] = {}
    topic_articles: dict[str, list[str]] = {}
    for aid in common:
        topic = llm[aid].get("topic", "unknown")
        if topic not in topic_agree:
            topic_agree[topic] = {"n": 0, "agree": 0}
            topic_articles[topic] = []
        topic_agree[topic]["n"] += 1
        topic_articles[topic].append(aid)
        ll = llm[aid].get("economic_relevance", "")
        tt = tfidf[aid].get("pred_label", "")
        if ll and tt and ll == tt:
            topic_agree[topic]["agree"] += 1

    for topic, stats in topic_agree.items():
        stats["agree_rate"] = round(stats["agree"] / stats["n"], 4) if stats["n"] > 0 else 0.0

    # LLM-labeled economic articles that TF-IDF missed (false negatives for TF-IDF)
    fn_articles = []
    for aid in common:
        ll = llm[aid].get("economic_relevance", "")
        tt = tfidf[aid].get("pred_label", "")
        if ll == "Economic" and tt == "Not Economic":
            fn_articles.append({
                "id": aid,
                "topic": llm[aid].get("topic", ""),
                "tfidf_score": tfidf[aid].get("score", 0.0),
                "notes": llm[aid].get("notes", ""),
            })

    # TF-IDF false positives (predicted Economic but LLM says Not Economic)
    fp_articles = []
    for aid in common:
        ll = llm[aid].get("economic_relevance", "")
        tt = tfidf[aid].get("pred_label", "")
        if ll == "Not Economic" and tt == "Economic":
            fp_articles.append({
                "id": aid,
                "topic": llm[aid].get("topic", ""),
                "tfidf_score": tfidf[aid].get("score", 0.0),
            })

    return {
        "n_common": len(common),
        "labels": labels,
        "confusion_matrix": cm,
        "cohens_kappa": kappa,
        "observed_agreement": round(obs_agree, 4),
        "classification_report": cr,
        "agreement_by_topic": topic_agree,
        "llm_economic_count": sum(1 for v in y_llm if v == "Economic"),
        "tfidf_economic_count": sum(1 for v in y_tfidf if v == "Economic"),
        "llm_base_rate": round(sum(1 for v in y_llm if v == "Economic") / len(y_llm), 4),
        "tfidf_base_rate": round(sum(1 for v in y_tfidf if v == "Economic") / len(y_tfidf), 4),
        "tfidf_false_negatives": fn_articles,
        "tfidf_false_positives": fp_articles,
    }


def analyze_keyword_filter(
    llm: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compare keyword_label (0/1) against LLM economic_relevance."""
    articles = []
    for aid, ann in llm.items():
        kw = ann.get("keyword_label", -1)
        ll = ann.get("economic_relevance", "")
        if kw >= 0 and ll:
            articles.append({"id": aid, "keyword": kw, "llm": ll})

    total = len(articles)
    kw_positive = sum(1 for a in articles if a["keyword"] == 1)
    kw_negative = total - kw_positive

    # Confusion: keyword -> Economic/Not Economic
    # LLM is reference
    tp = sum(1 for a in articles if a["keyword"] == 1 and a["llm"] == "Economic")
    fp = sum(1 for a in articles if a["keyword"] == 1 and a["llm"] == "Not Economic")
    fn = sum(1 for a in articles if a["keyword"] == 0 and a["llm"] == "Economic")
    tn = sum(1 for a in articles if a["keyword"] == 0 and a["llm"] == "Not Economic")

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    # Articles missed by keyword filter (LLM=Economic, keyword=0)
    fn_articles = [a for a in articles if a["keyword"] == 0 and a["llm"] == "Economic"]

    return {
        "total_articles": total,
        "keyword_positive": kw_positive,
        "keyword_negative": kw_negative,
        "llm_economic": tp + fn,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_negatives": [{"id": a["id"], "llm": a["llm"]} for a in fn_articles],
        "false_negative_count": len(fn_articles),
        "keyword_hit_rate": round(tp / kw_positive, 4) if kw_positive > 0 else 0.0,
    }


def analyze_economic_detail(
    llm: dict[str, dict[str, Any]],
    gold: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """For Economic articles, compute topic/sentiment/etc. distributions."""
    economic = {aid: ann for aid, ann in llm.items()
                if ann.get("economic_relevance") == "Economic"}

    topics = Counter()
    sentiments = Counter()
    narrative_forces = Counter()
    valuations = Counter()
    confidences = []

    for aid, ann in economic.items():
        t = ann.get("economic_topic")
        if t:
            topics[t] += 1
        s = ann.get("sentiment")
        if s:
            sentiments[s] += 1
        nf = ann.get("narrative_force")
        if nf:
            narrative_forces[nf] += 1
        v = ann.get("valuation_target")
        if v:
            valuations[v] += 1
        c = ann.get("confidence")
        if c is not None:
            confidences.append(c)

    # Topic distribution with article counts
    topic_articles: dict[str, list[dict]] = {}
    for aid, ann in economic.items():
        t = ann.get("economic_topic", "unknown")
        if t not in topic_articles:
            topic_articles[t] = []
        topic_articles[t].append({
            "id": aid,
            "sentiment": ann.get("sentiment"),
            "narrative_force": ann.get("narrative_force"),
            "notes": ann.get("notes", ""),
        })

    return {
        "n_economic": len(economic),
        "n_not_economic": sum(1 for a in llm.values() if a.get("economic_relevance") == "Not Economic"),
        "economic_base_rate": round(len(economic) / len(llm), 4) if llm else 0.0,
        "topic_distribution": dict(topics.most_common()),
        "sentiment_distribution": dict(sentiments.most_common()),
        "narrative_force_distribution": dict(narrative_forces.most_common()),
        "valuation_target_distribution": dict(valuations.most_common()),
        "confidence_stats": {
            "mean": round(sum(confidences) / len(confidences), 2) if confidences else None,
            "min": min(confidences) if confidences else None,
            "max": max(confidences) if confidences else None,
        },
        "topic_articles": topic_articles,
    }


def analyze_topic_distribution(
    llm: dict[str, dict[str, Any]],
    tfidf: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Analyze economic article distribution by BNLP topic."""
    topics_llm: dict[str, dict[str, int]] = {}
    for aid, ann in llm.items():
        topic = ann.get("topic", "unknown")
        if topic not in topics_llm:
            topics_llm[topic] = {"total": 0, "economic_llm": 0, "economic_tfidf": 0}
        topics_llm[topic]["total"] += 1
        if ann.get("economic_relevance") == "Economic":
            topics_llm[topic]["economic_llm"] += 1
        t = tfidf.get(aid, {}).get("pred_label", "")
        if t == "Economic":
            topics_llm[topic]["economic_tfidf"] += 1

    for topic, stats in topics_llm.items():
        stats["llm_econ_rate"] = round(stats["economic_llm"] / stats["total"], 4) if stats["total"] > 0 else 0.0
        stats["tfidf_econ_rate"] = round(stats["economic_tfidf"] / stats["total"], 4) if stats["total"] > 0 else 0.0

    return topics_llm


def analyze_self_consistency(
    pass1: dict[str, dict[str, Any]],
    pass2: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compare two annotation passes for self-consistency."""
    common = sorted(set(pass1.keys()) & set(pass2.keys()))
    field = "economic_relevance"

    y1, y2 = [], []
    for aid in common:
        v1 = pass1[aid].get(field)
        v2 = pass2[aid].get(field)
        if v1 and v2:
            y1.append(v1)
            y2.append(v2)

    if len(y1) < 2:
        return {"error": "Insufficient data for self-consistency", "n_common": len(common)}

    labels = sorted(set(y1) | set(y2))
    cm = confusion_matrix(y1, y2, labels)
    kappa = cohens_kappa(y1, y2)
    obs_agree = sum(1 for a, b in zip(y1, y2) if a == b) / len(y1)
    cr = classification_report(y1, y2, labels)

    # Article-level agreement
    article_agreement = []
    for aid in common:
        v1 = pass1[aid].get(field)
        v2 = pass2[aid].get(field)
        article_agreement.append({
            "id": aid,
            "pass1": v1,
            "pass2": v2,
            "agree": v1 == v2,
        })

    disagreements = [a for a in article_agreement if not a["agree"]]

    return {
        "n_common": len(common),
        "n_compared": len(y1),
        "labels": labels,
        "confusion_matrix": cm,
        "cohens_kappa": kappa,
        "observed_agreement": round(obs_agree, 4),
        "classification_report": cr,
        "disagreements": disagreements,
        "n_disagreements": len(disagreements),
    }


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("BENI Annotation Analysis")
    print("=" * 60)

    # ── Load data ────────────────────────────────────────────────────────
    print("\n[1/4] Loading data...")
    llm_path = EXPORTS_DIR / "llm_annotated_full.json"
    tfidf_path = EXPORTS_DIR / "beni_300_batch_with_ml.json"
    gold_path = EXPORTS_DIR / "gold_standard.json"

    if not llm_path.exists():
        print(f"  [ERROR] Missing: {llm_path}")
        sys.exit(1)
    if not tfidf_path.exists():
        print(f"  [ERROR] Missing: {tfidf_path}")
        sys.exit(1)

    llm = load_llm_annotations(llm_path)
    tfidf = load_tfidf_predictions(tfidf_path)
    gold = load_gold_standard(gold_path) if gold_path.exists() else {}

    print(f"  LLM annotations:  {len(llm)} articles")
    print(f"  TF-IDF predictions: {len(tfidf)} articles")
    print(f"  Gold standard:    {len(gold)} articles")

    # ── Phase 1: Economic Relevance Agreement ───────────────────────────
    print("\n[2/4] Computing LLM vs TF-IDF agreement...")
    relevance = analyze_economic_relevance(llm, tfidf)
    print(f"  Cohen's κ:           {relevance['cohens_kappa']}")
    print(f"  Observed agreement:  {relevance['observed_agreement']:.2%}")
    print(f"  LLM base rate:       {relevance['llm_base_rate']:.2%} ({relevance['llm_economic_count']} Economic)")
    print(f"  TF-IDF base rate:    {relevance['tfidf_base_rate']:.2%} ({relevance['tfidf_economic_count']} Economic)")
    print(f"  TF-IDF false neg:    {len(relevance['tfidf_false_negatives'])} articles")
    print(f"  TF-IDF false pos:    {len(relevance['tfidf_false_positives'])} articles")
    print(f"\n  Confusion Matrix (rows=LLM, cols=TF-IDF):")
    for t in relevance['labels']:
        row = []
        for p in relevance['labels']:
            row.append(str(relevance['confusion_matrix'][t][p]))
        print(f"    {t:>15s}: {', '.join(row)}")

    # ── Phase 2: Keyword Filter Analysis ────────────────────────────────
    print("\n[3/4] Analyzing keyword filter...")
    kw = analyze_keyword_filter(llm)
    print(f"  Keyword precision:  {kw['precision']:.2%}")
    print(f"  Keyword recall:     {kw['recall']:.2%}")
    print(f"  Keyword F1:         {kw['f1']:.2%}")
    print(f"  Keyword hit rate:   {kw['keyword_hit_rate']:.2%}")
    print(f"  False negatives:    {kw['false_negative_count']} (LLM-economic, keyword=0)")

    # ── Phase 3: Economic Detail ────────────────────────────────────────
    print("\n[4/4] Analyzing economic article detail...")
    detail = analyze_economic_detail(llm, gold)
    print(f"  Economic articles:   {detail['n_economic']}")
    print(f"  Base rate:           {detail['economic_base_rate']:.2%}")
    print(f"  Topics:              {detail['topic_distribution']}")
    print(f"  Sentiments:          {detail['sentiment_distribution']}")
    print(f"  Narrative forces:    {detail['narrative_force_distribution']}")

    # ── Topic Distribution ──────────────────────────────────────────────
    topic_dist = analyze_topic_distribution(llm, tfidf)

    # ── Build Report ────────────────────────────────────────────────────
    report = {
        "metadata": {
            "llm_source": str(llm_path),
            "tfidf_source": str(tfidf_path),
            "n_llm_articles": len(llm),
            "n_tfidf_articles": len(tfidf),
        },
        "economic_relevance_agreement": relevance,
        "keyword_filter_analysis": kw,
        "economic_detail": detail,
        "topic_distribution": topic_dist,
    }

    report_path = EXPORTS_DIR / "analysis_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nReport saved -> {report_path}")

    # ── Human-readable summary ──────────────────────────────────────────
    lines = [
        "=" * 60,
        "BENI Annotation Analysis Report",
        "=" * 60,
        "",
        f"LLM annotations:  {len(llm)} articles",
        f"TF-IDF predictions: {len(tfidf)} articles",
        "",
        "── Economic Relevance: LLM vs TF-IDF ──────────────────────────────",
        f"  Cohen's κ:           {relevance['cohens_kappa']}",
        f"  Observed agreement:  {relevance['observed_agreement']:.2%}",
        f"  LLM:                 {relevance['llm_economic_count']} Economic / {len(llm) - relevance['llm_economic_count']} Not",
        f"  TF-IDF:              {relevance['tfidf_economic_count']} Economic / {len(tfidf) - relevance['tfidf_economic_count']} Not",
        "",
        "  Classification Report (TF-IDF vs LLM reference):",
    ]
    for label, cr in relevance['classification_report'].items():
        lines.append(f"    {label:>15s}: p={cr['precision']:.4f} r={cr['recall']:.4f} f1={cr['f1']:.4f} n={cr['support']}")
    lines += [
        "",
        "── Keyword Filter Performance ─────────────────────────────────────",
        f"  Precision: {kw['precision']:.2%}",
        f"  Recall:    {kw['recall']:.2%}",
        f"  F1:        {kw['f1']:.2%}",
        f"  Missed:    {kw['false_negative_count']} economic articles",
        "",
        "── Economic Article Detail ────────────────────────────────────────",
        f"  Economic articles:   {detail['n_economic']}",
        f"  Base rate:           {detail['economic_base_rate']:.2%}",
        f"  Topics:              {json.dumps(detail['topic_distribution'])}",
        f"  Sentiments:          {json.dumps(detail['sentiment_distribution'])}",
        f"  Narrative forces:    {json.dumps(detail['narrative_force_distribution'])}",
        "",
    ]
    if 'confidence_stats' in detail and detail['confidence_stats']['mean'] is not None:
        lines += [
            f"  Confidence:          mean={detail['confidence_stats']['mean']} "
            f"min={detail['confidence_stats']['min']} max={detail['confidence_stats']['max']}",
            "",
        ]

    lines += [
        "── Topic Distribution ─────────────────────────────────────────────",
        f"  {'Topic':<20s} {'Total':>6s} {'Econ(LLM)':>10s} {'Econ(TFIDF)':>12s} {'LLM%':>7s} {'TFIDF%':>8s}",
        f"  {'-'*20} {'-'*6} {'-'*10} {'-'*12} {'-'*7} {'-'*8}",
    ]
    for topic in sorted(topic_dist.keys()):
        s = topic_dist[topic]
        lines.append(
            f"  {topic:<20s} {s['total']:>6d} {s['economic_llm']:>10d} {s['economic_tfidf']:>12d} "
            f"{s['llm_econ_rate']:>6.1%} {s['tfidf_econ_rate']:>7.1%}"
        )
    lines += ["", "=" * 60]

    txt_path = EXPORTS_DIR / "analysis_report.txt"
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Summary saved -> {txt_path}")

    # ── Self-consistency? ────────────────────────────────────────────────
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-consistency", type=Path, help="Path to second-pass annotations")
    args = parser.parse_args()

    if args.self_consistency and args.self_consistency.exists():
        print("\n\n" + "=" * 60)
        print("Self-Consistency Analysis")
        print("=" * 60)
        pass2 = load_second_pass(args.self_consistency)
        sc = analyze_self_consistency(llm, pass2)
        if "error" in sc:
            print(f"  [ERROR] {sc['error']}")
        else:
            print(f"  Common articles:     {sc['n_compared']}")
            print(f"  Cohen's κ:           {sc['cohens_kappa']}")
            print(f"  Observed agreement:  {sc['observed_agreement']:.2%}")
            print(f"  Disagreements:       {sc['n_disagreements']}")
            print(f"\n  Confusion Matrix:")
            for t in sc['labels']:
                row = []
                for p in sc['labels']:
                    row.append(str(sc['confusion_matrix'][t][p]))
                print(f"    {t:>15s}: {', '.join(row)}")
            if sc['n_disagreements'] > 0:
                print(f"\n  Disagreements:")
                for d in sc['disagreements']:
                    print(f"    {d['id']:>20s}: pass1={d['pass1']:>15s}  pass2={d['pass2']:>15s}")

            # Append self-consistency to report file
            report["self_consistency"] = sc
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"\nUpdated report -> {report_path}")


if __name__ == "__main__":
    main()
