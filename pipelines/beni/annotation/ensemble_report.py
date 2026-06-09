"""
Ensemble Agreement Report for BENI Multi-LLM Annotation.

Computes paper-ready statistics from the open-source 3-LLM ensemble:
  - Pairwise Cohen's kappa (observed + chance-corrected, with p-values)
  - Fleiss' kappa for multi-rater agreement
  - Agreement stratified by article topic
  - Confidence calibration (does confidence predict agreement?)
  - Vote margin distribution
  - Disagreement audit
  - LaTeX-ready table output for the paper

Usage:
    # Point at the consensus output
    python3 ensemble_report.py \
        --input exports/ensemble_results/ensemble_consensus.json \
        --log exports/ensemble_results/ensemble_log.json

    # Generate LaTeX tables
    python3 ensemble_report.py --latex
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

_HERE = Path(__file__).parent.resolve()
DEFAULT_CONSENSUS = _HERE / "exports" / "ensemble_results" / "ensemble_consensus.json"
DEFAULT_LOG = _HERE / "exports" / "ensemble_results" / "ensemble_log.json"
DEFAULT_BATCH = _HERE / "exports" / "beni_300_batch.json"


# ── Kappa implementations ───────────────────────────────────────────

def cohens_kappa(y1: list[str], y2: list[str]) -> dict[str, float]:
    """Cohen's kappa with SE, z, and p-value."""
    n = len(y1)
    if n == 0:
        return {"kappa": 0.0, "observed_agreement": 0.0, "n": 0}

    labels = sorted(set(y1) | set(y2))
    po = sum(1 for a, b in zip(y1, y2) if a == b) / n
    c1 = Counter(y1)
    c2 = Counter(y2)
    pe = sum((c1.get(l, 0) / n) * (c2.get(l, 0) / n) for l in labels)

    kappa = 1.0 if abs(pe - 1.0) < 1e-9 else (po - pe) / (1 - pe)

    p1 = {l: c1.get(l, 0) / n for l in labels}
    p2 = {l: c2.get(l, 0) / n for l in labels}
    se_null = 0.0
    z = 0.0
    p_value = 1.0
    if abs(pe - 1.0) > 1e-9:
        try:
            se_null = math.sqrt(
                (pe + pe**2 - sum(p1[l] * p2[l] * (p1[l] + p2[l]) for l in labels))
                / (n * (1 - pe) ** 2)
            )
            z = kappa / se_null if se_null > 0 else 0.0
            p_value = 2 * (1 - _norm_cdf(abs(z)))
        except (ValueError, ZeroDivisionError):
            pass

    cm = {l1: {l2: 0 for l2 in labels} for l1 in labels}
    for a, b in zip(y1, y2):
        cm[a][b] += 1

    return {
        "kappa": round(kappa, 4),
        "observed_agreement": round(po, 4),
        "n": n,
        "se_null": round(se_null, 6),
        "z": round(z, 4),
        "p_value": round(p_value, 6),
        "labels": labels,
        "confusion_matrix": cm,
    }


def fleiss_kappa(ratings: list[list[str]]) -> dict[str, float]:
    """Fleiss' kappa for multiple raters."""
    n_articles = len(ratings)
    if n_articles == 0:
        return {"kappa": 0.0, "n_articles": 0, "n_raters": 0}

    n_raters = len(ratings[0]) if ratings else 0
    if n_raters < 2:
        return {"kappa": 0.0, "n_articles": n_articles, "n_raters": n_raters}

    all_labels = sorted(set(l for article in ratings for l in article))
    k = len(all_labels)
    label_idx = {l: i for i, l in enumerate(all_labels)}

    n_matrix = [[0] * k for _ in range(n_articles)]
    for i, article in enumerate(ratings):
        for r in article:
            if r in label_idx:
                n_matrix[i][label_idx[r]] += 1

    P = []
    for i in range(n_articles):
        total = sum(n_matrix[i])
        if total < 2:
            P.append(0.0)
            continue
        sum_sq = sum(n_matrix[i][j] ** 2 for j in range(k))
        P.append((sum_sq - total) / (total * (total - 1)))

    P_bar = sum(P) / n_articles if n_articles > 0 else 0.0
    total_assignments = n_articles * n_raters
    p_j = [sum(n_matrix[i][j] for i in range(n_articles)) / total_assignments for j in range(k)]
    P_e_bar = sum(pj ** 2 for pj in p_j)

    kappa = 1.0 if abs(P_e_bar - 1.0) < 1e-9 else (P_bar - P_e_bar) / (1 - P_e_bar)

    var_P_e_bar = (2 * (sum(pj * (1 - pj) for pj in p_j) - P_e_bar * (1 - P_e_bar))) / (
        n_articles * n_raters * (n_raters - 1)
    ) if n_articles * n_raters * (n_raters - 1) > 0 else 0.0
    se = math.sqrt(var_P_e_bar) / ((1 - P_e_bar) ** 2) if abs(P_e_bar - 1.0) > 1e-9 and var_P_e_bar >= 0 else 0.0

    ci_lower = max(-1.0, kappa - 1.96 * se) if se > 0 else -1.0
    ci_upper = min(1.0, kappa + 1.96 * se) if se > 0 else 1.0

    return {
        "kappa": round(kappa, 4),
        "P_bar": round(P_bar, 4),
        "P_e_bar": round(P_e_bar, 4),
        "n_articles": n_articles,
        "n_raters": n_raters,
        "n_categories": k,
        "standard_error": round(se, 6),
        "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
    }


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ── Loaders ─────────────────────────────────────────────────────────

def load_consensus(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_log(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_batch_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"]: item for item in data}


# ── Analyses ────────────────────────────────────────────────────────

def analyze_pairwise(consensus: list[dict[str, Any]]) -> dict[str, Any]:
    first = consensus[0]
    model_names = sorted(first.get("provider_labels", {}).keys())
    pairwise = {}
    for i, p1 in enumerate(model_names):
        for p2 in model_names[i + 1:]:
            y1, y2 = [], []
            for article in consensus:
                labels = article.get("provider_labels", {})
                l1, l2 = labels.get(p1), labels.get(p2)
                if l1 in ("Economic", "Not Economic") and l2 in ("Economic", "Not Economic"):
                    y1.append(l1)
                    y2.append(l2)
            pairwise[f"{p1}_vs_{p2}"] = cohens_kappa(y1, y2)
    return pairwise


def analyze_three_way(consensus: list[dict[str, Any]]) -> dict[str, Any]:
    all_ratings = []
    for article in consensus:
        labels = [v for v in article.get("provider_labels", {}).values()
                  if v in ("Economic", "Not Economic")]
        if len(labels) >= 2:
            all_ratings.append(labels)
    fleiss = fleiss_kappa(all_ratings)

    n = len(consensus)
    counts = Counter(a.get("ensemble", {}).get("agreement_type", "unknown") for a in consensus)
    breakdown = {}
    for level in ["full_agreement", "majority", "full_disagreement"]:
        c = counts.get(level, 0)
        breakdown[level] = {"count": c, "pct": round(c / n * 100, 1) if n else 0}

    return {"fleiss_kappa": fleiss, "three_way_breakdown": breakdown}


def analyze_by_topic(
    consensus: list[dict[str, Any]],
    batch_index: dict[str, Any],
) -> dict[str, Any]:
    topic_stats = {}
    for article in consensus:
        aid = article["id"]
        batch_item = batch_index.get(aid, {})
        topic = batch_item.get("data", {}).get("topic", "unknown")
        agree_type = article.get("ensemble", {}).get("agreement_type", "unknown")

        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "full_agreement": 0, "majority": 0, "full_disagreement": 0}
        topic_stats[topic]["total"] += 1
        topic_stats[topic][agree_type] += 1

    for t, s in topic_stats.items():
        s["full_agreement_pct"] = round(s["full_agreement"] / s["total"] * 100, 1) if s["total"] else 0
        s["majority_pct"] = round(s["majority"] / s["total"] * 100, 1) if s["total"] else 0
        s["full_disagreement_pct"] = round(s["full_disagreement"] / s["total"] * 100, 1) if s["total"] else 0
    return topic_stats


def analyze_confidence_calibration(consensus: list[dict[str, Any]]) -> dict[str, Any]:
    conf_by_agree = defaultdict(list)
    for article in consensus:
        details = article.get("provider_details", {})
        agree_type = article.get("ensemble", {}).get("agreement_type", "unknown")
        confs = [p.get("confidence") for p in details.values()
                 if isinstance(p.get("confidence"), (int, float))]
        if confs:
            conf_by_agree[agree_type].append(sum(confs) / len(confs))

    stats = {}
    for atype, confs in conf_by_agree.items():
        stats[atype] = {
            "n": len(confs),
            "mean": round(sum(confs) / len(confs), 2),
            "min": min(confs),
            "max": max(confs),
        }
    return {"confidence_by_agreement": stats}


def analyze_margins(consensus: list[dict[str, Any]]) -> dict[str, Any]:
    margins = [a.get("ensemble", {}).get("vote_margin", 0) for a in consensus]
    margin_counts = Counter(margins)
    return {
        "distribution": dict(margin_counts.most_common()),
        "mean_margin": round(sum(margins) / len(margins), 2) if margins else 0,
        "n_unanimous_3": margin_counts.get(3, 0) if 3 in margin_counts else 0,
        "n_2_1_splits": sum(v for k, v in margin_counts.items() if k == 1) if 1 in margin_counts else 0,
    }


def list_disagreements(
    consensus: list[dict[str, Any]],
    batch_index: dict[str, Any],
    max_count: int = 30,
) -> list[dict[str, Any]]:
    result = []
    for article in consensus:
        atype = article.get("ensemble", {}).get("agreement_type", "")
        if atype in ("majority", "full_disagreement"):
            aid = article["id"]
            batch = batch_index.get(aid, {})
            text = (batch.get("data", {}).get("text", "") or "")[:200]
            result.append({
                "id": aid,
                "agreement_type": atype,
                "provider_labels": article.get("provider_labels", {}),
                "consensus_label": article.get("ensemble", {}).get("economic_relevance"),
                "vote_distribution": article.get("ensemble", {}).get("vote_distribution"),
                "topic": batch.get("data", {}).get("topic", ""),
                "text_preview": text,
            })
        if len(result) >= max_count:
            break
    return result


# ── LaTeX tables ────────────────────────────────────────────────────

def _latex_escape(s: str) -> str:
    return s.replace("_", "\\_").replace("%", "\\%")


def generate_latex_tables(report: dict[str, Any]) -> str:
    lines = [
        r"% LaTeX tables generated by BENI ensemble_report.py",
        r"% Include in paper Methods or Results section.",
        "",
    ]
    pairwise = report.get("pairwise_agreement", {})
    if pairwise:
        lines += [
            r"\begin{table}[h]",
            r"\centering",
            r"\caption{Pairwise LLM Agreement on Economic Relevance}",
            r"\label{tab:ensemble-agreement}",
            r"\begin{tabular}{lccccc}",
            r"\toprule",
            r"Pair & Observed & $\kappa$ & SE & $z$ & $p$ \\",
            r"\midrule",
        ]
        for pair, stats in pairwise.items():
            name = pair.replace("_vs_", " vs ")
            lines.append(
                rf"{name} & {stats['observed_agreement']:.1%} & "
                rf"{stats['kappa']:.3f} & {stats.get('se_null', 0):.4f} & "
                rf"{stats.get('z', 0):.2f} & {stats.get('p_value', 1):.4f} \\"
            )
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]

    three_way = report.get("three_way_agreement", {}).get("three_way_breakdown", {})
    fleiss = report.get("three_way_agreement", {}).get("fleiss_kappa", {})
    if three_way:
        lines += [
            r"\begin{table}[h]",
            r"\centering",
            r"\caption{Three-Way LLM Agreement}",
            r"\label{tab:three-way-agreement}",
            r"\begin{tabular}{lcc}",
            r"\toprule",
            r"Agreement Level & Articles & \% \\",
            r"\midrule",
        ]
        for level in ["full_agreement", "majority", "full_disagreement"]:
            if level in three_way:
                label = level.replace("_", " ").title()
                lines.append(rf"{label} & {three_way[level]['count']} & {three_way[level]['pct']}\% \\")
        ci = fleiss.get("ci_95", ["N/A", "N/A"])
        lines += [
            r"\midrule",
            rf"Fleiss' $\kappa$ & \multicolumn{{2}}{{c}}{{{fleiss.get('kappa', 'N/A')} "
            rf"(95\% CI: {ci[0]}--{ci[1]})}} \\",
            r"\bottomrule", r"\end{tabular}", r"\end{table}", ""
        ]

    topic_agree = report.get("agreement_by_topic", {})
    if topic_agree:
        lines += [
            r"\begin{table}[h]",
            r"\centering",
            r"\caption{LLM Agreement by Article Topic}",
            r"\label{tab:agreement-by-topic}",
            r"\begin{tabular}{lcccc}",
            r"\toprule",
            r"Topic & N & Full Agreement & Majority & Disagreement \\",
            r"\midrule",
        ]
        for topic in sorted(topic_agree.keys()):
            s = topic_agree[topic]
            lines.append(
                rf"{_latex_escape(topic)} & {s['total']} & "
                rf"{s['full_agreement']} ({s['full_agreement_pct']}\%) & "
                rf"{s['majority']} ({s['majority_pct']}\%) & "
                rf"{s['full_disagreement']} ({s['full_disagreement_pct']}\%) \\"
            )
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]

    conf = report.get("confidence_calibration", {}).get("confidence_by_agreement", {})
    if conf:
        lines += [
            r"\begin{table}[h]",
            r"\centering",
            r"\caption{Mean LLM Confidence by Agreement Level}",
            r"\label{tab:confidence-calibration}",
            r"\begin{tabular}{lccc}",
            r"\toprule",
            r"Agreement Level & N & Mean Confidence & Range \\",
            r"\midrule",
        ]
        for level in ["full_agreement", "majority", "full_disagreement"]:
            if level in conf:
                s = conf[level]
                label = level.replace("_", " ").title()
                lines.append(rf"{label} & {s['n']} & {s['mean']:.2f} & {s['min']}--{s['max']} \\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BENI ensemble agreement report")
    parser.add_argument("--input", type=Path, default=DEFAULT_CONSENSUS,
                        help="Ensemble consensus JSON")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG,
                        help="Ensemble log JSON")
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH,
                        help="Original batch JSON for topic info")
    parser.add_argument("--output-dir", type=Path, default=_HERE / "exports",
                        help="Output directory")
    parser.add_argument("--latex", action="store_true",
                        help="Generate LaTeX tables")
    parser.add_argument("--max-disagreements", type=int, default=20)
    args = parser.parse_args()

    print("=" * 60)
    print("BENI Ensemble Agreement Report")
    print("=" * 60)

    if not args.input.exists():
        print(f"[ERROR] Consensus not found: {args.input}")
        print("Run multi_llm_ensemble.py first.")
        sys.exit(1)

    consensus = load_consensus(args.input)
    log = load_log(args.log)
    batch_index = load_batch_index(args.batch)
    n = len(consensus)

    print(f"\nLoaded {n} consensus articles")
    print(f"Models: {log.get('metrics', {}).get('model_names', 'unknown')}")

    report: dict[str, Any] = {
        "metadata": {"n_articles": n, "log": log},
    }

    # 1. Pairwise
    print("\n[1/5] Pairwise Cohen's kappa...")
    pairwise = analyze_pairwise(consensus)
    report["pairwise_agreement"] = pairwise
    for pair, stats in pairwise.items():
        print(f"  {pair:>25s}: κ={stats['kappa']:.4f}, agree={stats['observed_agreement']:.2%}, p={stats['p_value']:.4f}")

    # 2. Three-way
    print("\n[2/5] Three-way agreement (Fleiss' κ)...")
    three_way = analyze_three_way(consensus)
    report["three_way_agreement"] = three_way
    fk = three_way["fleiss_kappa"]
    print(f"  Fleiss' κ: {fk['kappa']}  (95% CI: {fk['ci_95'][0]}–{fk['ci_95'][1]})")
    for level, stats in three_way["three_way_breakdown"].items():
        print(f"  {level:<25s}: {stats['count']:>4d} ({stats['pct']:.1f}%)")

    # 3. By topic
    print("\n[3/5] Agreement by topic...")
    topic_agree = analyze_by_topic(consensus, batch_index)
    report["agreement_by_topic"] = topic_agree
    print(f"  {'Topic':<20s} {'N':>4s} {'Full%':>7s} {'Maj%':>6s} {'Dis%':>6s}")
    print(f"  {'-'*43}")
    for t in sorted(topic_agree.keys()):
        s = topic_agree[t]
        print(f"  {t:<20s} {s['total']:>4d} {s['full_agreement_pct']:>6.1f}% {s['majority_pct']:>5.1f}% {s['full_disagreement_pct']:>5.1f}%")

    # 4. Confidence calibration
    print("\n[4/5] Confidence calibration...")
    conf_cal = analyze_confidence_calibration(consensus)
    report["confidence_calibration"] = conf_cal
    for atype, stats in conf_cal.get("confidence_by_agreement", {}).items():
        print(f"  {atype:<25s}: mean={stats['mean']:.2f} (n={stats['n']})")

    # 5. Margins + disagreements
    margins = analyze_margins(consensus)
    report["vote_margin_distribution"] = margins
    print(f"\n  Margins: mean={margins['mean_margin']:.2f}, "
          f"unanimous 3/3={margins['n_unanimous_3']}, 2-1 splits={margins['n_2_1_splits']}")

    print("\n[5/5] Listing disagreements...")
    disagreements = list_disagreements(consensus, batch_index, max_count=args.max_disagreements)
    report["disagreement_articles"] = disagreements
    if disagreements:
        print(f"  First {len(disagreements)}:")
        for d in disagreements:
            print(f"    {d['id'][:24]:<24s} {d['agreement_type']:<18s} "
                  f"{d['provider_labels']} → {d['consensus_label']}")

    # ── Save ────────────────────────────────────────────────────────
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "ensemble_agreement_report.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Human-readable
    lines = [
        "=" * 60,
        "BENI Multi-LLM Ensemble Agreement Report",
        "=" * 60,
        "",
        f"Articles: {n}",
        f"Models:   {log.get('metrics', {}).get('model_names', '?')}",
        "",
        "── Pairwise Agreement (Cohen's κ) ──────────────────────────────",
    ]
    for pair, stats in pairwise.items():
        lines.append(
            f"  {pair:<25s}: κ = {stats['kappa']:.4f}, "
            f"observed = {stats['observed_agreement']:.2%}, "
            f"p = {stats['p_value']:.4f}"
        )
    lines += [
        "",
        "── Three-Way Agreement (Fleiss' κ) ─────────────────────────────",
        f"  Fleiss' κ:        {fk['kappa']}",
        f"  P_bar (observed): {fk['P_bar']:.4f}",
        f"  P_e_bar (chance): {fk['P_e_bar']:.4f}",
        f"  95% CI:           {fk['ci_95'][0]} — {fk['ci_95'][1]}",
        "",
        "  Breakdown:",
    ]
    for level, stats in three_way["three_way_breakdown"].items():
        lines.append(f"    {level:<25s}: {stats['count']:>4d} ({stats['pct']:.1f}%)")
    lines += [
        "",
        "── Vote Margins ────────────────────────────────────────────────",
        f"  Mean margin:           {margins['mean_margin']:.2f}",
        f"  3/3 unanimous:         {margins['n_unanimous_3']}",
        f"  2/1 split:             {margins['n_2_1_splits']}",
        "",
        "── Agreement by Topic ──────────────────────────────────────────",
        f"  {'Topic':<20s} {'N':>4s} {'Full%':>7s} {'Maj%':>6s} {'Dis%':>6s}",
        f"  {'-'*43}",
    ]
    for t in sorted(topic_agree.keys()):
        s = topic_agree[t]
        lines.append(f"  {t:<20s} {s['total']:>4d} {s['full_agreement_pct']:>6.1f}% {s['majority_pct']:>5.1f}% {s['full_disagreement_pct']:>5.1f}%")
    lines += [
        "",
        "── Confidence Calibration ──────────────────────────────────────",
        f"  {'Level':<25s} {'N':>4s} {'Mean':>6s} {'Range':>10s}",
        f"  {'-'*45}",
    ]
    for level in ["full_agreement", "majority", "full_disagreement"]:
        if level in conf_cal.get("confidence_by_agreement", {}):
            s = conf_cal["confidence_by_agreement"][level]
            lines.append(f"  {level.replace('_', ' ').title():<25s} {s['n']:>4d} {s['mean']:>6.2f} {s['min']}–{s['max']}")
    if disagreements:
        lines += ["", "── Disagreements (sample) ─────────────────────────────────────"]
        for d in disagreements[:10]:
            lines.append(f"  {d['id'][:24]:<24s} {d['agreement_type']:<18s} {d['provider_labels']}")
    lines += [
        "",
        "─" * 60,
        "Methods sentence for the paper:",
        "─" * 60,
        "",
    ]
    names = log.get("metrics", {}).get("model_names", [])
    fk_kappa = fk.get("kappa", "N/A")
    fk_ci = fk.get("ci_95", ["N/A", "N/A"])
    three_full = three_way["three_way_breakdown"].get("full_agreement", {})
    if pairwise:
        kappas = [s["kappa"] for s in pairwise.values()]
        lines.append(
            f"Three open-source LLMs ({', '.join(names)}) independently annotated {n} "
            f"Bengali news articles for economic relevance. Pairwise Cohen's kappa ranged from "
            f"{min(kappas):.3f} to {max(kappas):.3f}; "
            f"Fleiss' multi-rater kappa = {fk_kappa} "
            f"(95% CI: {fk_ci[0]}–{fk_ci[1]}). "
            f"Full three-way agreement was achieved on {three_full.get('count', 0)} of {n} articles "
            f"({three_full.get('pct', 0):.0f}%)."
        )
    lines += ["", "=" * 60]

    txt_path = args.output_dir / "ensemble_agreement_report.txt"
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport -> {json_path.name}, {txt_path.name}")

    if args.latex:
        latex = generate_latex_tables(report)
        latex_path = args.output_dir / "ensemble_latex_tables.tex"
        latex_path.write_text(latex, encoding="utf-8")
        print(f"LaTeX  -> {latex_path.name}")

    print("=" * 60)


if __name__ == "__main__":
    main()
