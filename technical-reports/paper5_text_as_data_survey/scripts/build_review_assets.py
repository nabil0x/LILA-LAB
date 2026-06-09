from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paper5-text-as-data")

import matplotlib.pyplot as plt
import pandas as pd


PAPER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PAPER_ROOT / "data" / "seed_literature_database.csv"
DEFAULT_RESULTS = PAPER_ROOT / "results"

ERA_ORDER = [
    "content_analysis_1916_1950",
    "quant_content_1950_1980",
    "computer_assisted_1980_2000",
    "dictionary_2000_2010",
    "topic_ml_2010_2018",
    "transformers_2018_2022",
    "llm_2022_2026",
]

ERA_LABELS = {
    "content_analysis_1916_1950": "Content analysis\n1916-1950",
    "quant_content_1950_1980": "Quant content\n1950-1980",
    "computer_assisted_1980_2000": "Computer-assisted\n1980-2000",
    "dictionary_2000_2010": "Dictionaries\n2000-2010",
    "topic_ml_2010_2018": "Topics + ML\n2010-2018",
    "transformers_2018_2022": "Transformers\n2018-2022",
    "llm_2022_2026": "LLMs\n2022-2026",
}


def load_database(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
    df["era"] = pd.Categorical(df["era"], categories=ERA_ORDER, ordered=True)
    return df.sort_values(["year", "paper_id"]).reset_index(drop=True)


def count_table(df: pd.DataFrame, column: str, name: str, out_dir: Path) -> pd.DataFrame:
    table = (
        df[column]
        .value_counts()
        .rename_axis(column)
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .reset_index(drop=True)
    )
    table.to_csv(out_dir / f"{name}.csv", index=False)
    write_latex(table, out_dir / f"{name}.tex")
    return table


def write_latex(df: pd.DataFrame, path: Path) -> None:
    safe = df.copy()
    safe.columns = [str(c).replace("_", "\\_") for c in safe.columns]
    for col in safe.select_dtypes(include=["object", "category"]).columns:
        safe[col] = safe[col].astype(str).str.replace("_", "\\_", regex=False)
    path.write_text(safe.to_latex(index=False, escape=False), encoding="utf-8")


def build_tables(df: pd.DataFrame, tables_dir: Path) -> dict[str, int]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "n_seed_papers": int(len(df)),
        "start_year": int(df["year"].min()),
        "end_year": int(df["year"].max()),
        "n_disciplines": int(df["discipline"].nunique()),
        "n_method_families": int(df["method_family"].nunique()),
    }

    era_table = (
        df.groupby("era", observed=False)
        .size()
        .rename("n")
        .reset_index()
    )
    era_table["era_label"] = era_table["era"].astype(str).map(ERA_LABELS)
    era_table = era_table[["era", "era_label", "n"]]
    era_table.to_csv(tables_dir / "era_counts.csv", index=False)
    write_latex(era_table, tables_dir / "era_counts.tex")

    count_table(df, "discipline", "discipline_counts", tables_dir)
    count_table(df, "method_family", "method_counts", tables_dir)
    count_table(df, "validation", "validation_counts", tables_dir)
    count_table(df, "language", "language_counts", tables_dir)

    cross = pd.crosstab(df["discipline"], df["era"])
    cross = cross.reindex(columns=ERA_ORDER, fill_value=0)
    cross.to_csv(tables_dir / "discipline_by_era.csv")
    write_latex(cross.reset_index(), tables_dir / "discipline_by_era.tex")

    taxonomy = (
        df.groupby(["method_family", "task"], observed=True)
        .size()
        .rename("n")
        .reset_index()
        .sort_values(["method_family", "n"], ascending=[True, False])
    )
    taxonomy.to_csv(tables_dir / "method_task_taxonomy.csv", index=False)
    write_latex(taxonomy, tables_dir / "method_task_taxonomy.tex")
    return summary


def plot_timeline(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    y_positions = {era: i for i, era in enumerate(ERA_ORDER)}
    colors = {
        "Political Science": "#1f77b4",
        "Communication": "#ff7f0e",
        "Economics": "#2ca02c",
        "Psychology": "#d62728",
        "Computational Social Science": "#9467bd",
        "NLP": "#8c564b",
    }
    for _, row in df.iterrows():
        ax.scatter(
            row["year"],
            y_positions[str(row["era"])],
            s=80,
            color=colors.get(row["discipline"], "#7f7f7f"),
            alpha=0.85,
        )
        if row["paper_id"] in {"lasswell_1927", "stone_1966", "tetlock_2007", "grimmer_2013", "devlin_2019", "gilardi_2023", "nabil_beni_2026"}:
            ax.text(row["year"] + 0.5, y_positions[str(row["era"])] + 0.05, row["authors"].split()[0], fontsize=8)
    ax.set_yticks(range(len(ERA_ORDER)))
    ax.set_yticklabels([ERA_LABELS[e] for e in ERA_ORDER])
    ax.set_xlabel("Year")
    ax.set_title("Seed timeline of text-as-data methods in social science")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_method_adoption(df: pd.DataFrame, path: Path) -> None:
    yearly = df.groupby(["year", "method_family"]).size().rename("n").reset_index()
    pivot = yearly.pivot_table(index="year", columns="method_family", values="n", fill_value=0)
    pivot = pivot.sort_index().cumsum()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker="o", linewidth=1.7, label=col.replace("_", " "))
    ax.set_title("Cumulative method-family adoption in the seed database")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative papers")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_validation(df: pd.DataFrame, path: Path) -> None:
    table = pd.crosstab(df["discipline"], df["validation"])
    fig, ax = plt.subplots(figsize=(11, 5.5))
    table.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_title("Validation standards by discipline in the seed database")
    ax.set_xlabel("Discipline")
    ax.set_ylabel("Papers")
    ax.legend(frameon=False, fontsize=7, bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_language_gap(df: pd.DataFrame, path: Path) -> None:
    counts = df["language"].value_counts()
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(counts.index, counts.values, color=["#1f77b4", "#ff7f0e", "#2ca02c"][: len(counts)])
    ax.set_title("Language coverage in the seed database")
    ax.set_ylabel("Papers")
    ax.set_xlabel("Language coverage")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def plot_llm_matrix(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.axhline(0.5, color="black", linewidth=1)
    ax.axvline(0.5, color="black", linewidth=1)
    ax.text(0.25, 0.75, "High promise\nLow current reliability\nLLM annotation\nNarrative coding", ha="center", va="center", fontsize=10)
    ax.text(0.75, 0.75, "High promise\nHigh reliability target\nHuman-audited LLM pipelines\nMultilingual monitoring", ha="center", va="center", fontsize=10)
    ax.text(0.25, 0.25, "Low promise\nLow reliability\nUnvalidated synthetic inference", ha="center", va="center", fontsize=10)
    ax.text(0.75, 0.25, "Operationally useful\nNarrow tasks\nDictionary replacement\nPre-screening", ha="center", va="center", fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0.25, 0.75])
    ax.set_xticklabels(["Low validation", "High validation"])
    ax.set_yticks([0.25, 0.75])
    ax.set_yticklabels(["Low substantive complexity", "High substantive complexity"])
    ax.set_title("LLM capabilities versus social-science measurement needs")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Paper 5 review tables and figures")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()

    tables_dir = args.results_dir / "tables"
    figures_dir = args.results_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = load_database(args.database)
    summary = build_tables(df, tables_dir)
    plot_timeline(df, figures_dir / "timeline_seed.png")
    plot_method_adoption(df, figures_dir / "method_adoption_seed.png")
    plot_validation(df, figures_dir / "validation_by_discipline.png")
    plot_language_gap(df, figures_dir / "language_gap_seed.png")
    plot_llm_matrix(figures_dir / "llm_capability_matrix.png")

    summary["outputs"] = {
        "tables": str(tables_dir),
        "figures": str(figures_dir),
    }
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
