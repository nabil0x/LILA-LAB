"""
Prepare a single directory with all data needed for Kaggle.

Usage:
    python3 prepare_kaggle_data.py

Output:
    Creates ../../data/kaggle/beni-data/ with this structure:

    beni-data/
    ├── potrika/       # All 39 Potrika CSV files (3.3 GB)
    ├── macro/         # Macroeconomic indicators (4 CSVs)
    ├── models/        # Trained TF-IDF model
    └── outputs/       # Previous index + correlations (continuity)

Then zip it:
    cd ../../data/kaggle/
    zip -r beni-data.zip beni-data/

Upload beni-data.zip as a Kaggle Dataset (private).
"""

import shutil
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).resolve().parent
BENI_PILOT = SCRIPT_DIR.parent / "beni_pilot"
ROOT = BENI_PILOT.parent
PROJECT_ROOT = ROOT.parent  # beni/
OUT = ROOT / "data" / "kaggle" / "beni-data"


def copy_tree(src: Path, dst: Path, desc: str) -> int:
    """Copy contents of src into dst. Returns file count."""
    if not src.exists():
        print(f"  SKIP ({desc}): {src} not found")
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in src.iterdir():
        if item.is_file():
            shutil.copy2(item, dst / item.name)
            count += 1
    print(f"  {desc}: {count} files -> {dst}")
    return count


def main() -> None:
    print(f"Preparing Kaggle data bundle at: {OUT}\n", flush=True)
    total = 0

    # 1. Potrika CSVs
    potrika_src = ROOT / "data" / "raw" / "potrika"
    total += copy_tree(potrika_src, OUT / "potrika", "Potrika CSVs")

    # 2. Macro CSVs
    macro_src = PROJECT_ROOT / "data" / "raw" / "macro"
    total += copy_tree(macro_src, OUT / "macro", "Macro CSVs")

    # 3. Trained TF-IDF model
    model_src = ROOT / "outputs" / "models" / "economic_potrika-timeseries_tfidf_logreg.joblib"
    if model_src.exists():
        (OUT / "models").mkdir(parents=True, exist_ok=True)
        shutil.copy2(model_src, OUT / "models" / model_src.name)
        total += 1
        print(f"  TF-IDF model: 1 file -> {OUT / 'models'}")
    else:
        print(f"  SKIP (model): {model_src} not found")

    # 4. Previous narrative index + correlations (optional, for continuity)
    index_src = ROOT / "outputs" / "index"
    total += copy_tree(index_src, OUT / "outputs" / "index", "Narrative index")

    # 5. BanglaBERT model — NOT included.
    # Download from Hugging Face in the Kaggle notebook:
    #   from transformers import ElectraForSequenceClassification, ElectraTokenizerFast
    #   model = ElectraForSequenceClassification.from_pretrained("csebuetnlp/banglabert", num_labels=2)
    print("\n  BanglaBERT model: NOT included (download from Hugging Face in notebook)", flush=True)

    print(f"\nDone. {total} files copied to {OUT}", flush=True)
    print("\nTo create the Kaggle Dataset:", flush=True)
    print(f"  cd {OUT.parent}", flush=True)
    print("  zip -r beni-data.zip beni-data/", flush=True)
    print("Then upload beni-data.zip as a private Kaggle Dataset.", flush=True)
    print("\nIn the notebook, data will be at: /kaggle/input/beni-data/", flush=True)


if __name__ == "__main__":
    main()
