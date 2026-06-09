from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42

    # --- Data paths (override these for Kaggle) ---
    raw_data_dir: Path = ROOT / "data" / "raw" / "news_categorization"
    potrika_dir: Path = ROOT / "data" / "raw" / "potrika"
    potrika_processed: Path = ROOT / "data" / "processed" / "potrika_economy.csv"
    macro_dir: Path = ROOT.parent / "data" / "raw" / "macro"

    # --- Output paths ---
    output_dir: Path = ROOT / "outputs"
    model_dir: Path = ROOT / "outputs" / "models"
    report_dir: Path = ROOT / "outputs" / "reports"

    # --- Model paths ---
    banglabert_dir: Path = ROOT / "models" / "csebuetnlp-banglabert"

    # --- TF-IDF hyperparameters ---
    max_features: int = 80_000
    min_df: int = 2
    ngram_min: int = 1
    ngram_max: int = 2
    max_iter: int = 1_000
    target_task: str = "topic"

    # --- Potrika timeseries split dates ---
    potrika_train_end: str = "2018-12-31"
    potrika_val_end: str = "2019-12-31"

    # --- BanglaBERT hyperparameters ---
    banglabert_epochs: int = 3
    banglabert_batch_size: int = 4
    banglabert_max_len: int = 384
    banglabert_learning_rate: float = 2e-5


ECONOMIC_KEYWORDS = [
    "অর্থনীতি",
    "অর্থনৈতিক",
    "মুদ্রাস্ফীতি",
    "মূল্যস্ফীতি",
    "ভোক্তা মূল্য",
    "খাদ্য মূল্য",
    "ডলার",
    "বৈদেশিক মুদ্রা",
    "রিজার্ভ",
    "বাংলাদেশ ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "সুদের হার",
    "ব্যাংক ঋণ",
    "বিনিয়োগ",
    "বিনিয়োগ",
    "রপ্তানি",
    "আমদানি",
    "রেমিট্যান্স",
    "রাজস্ব",
    "জাতীয় বাজেট",
    "জাতীয় বাজেট",
    "জিডিপি",
    "মোট দেশজ উৎপাদন",
    "পুঁজিবাজার",
    "শেয়ারবাজার",
    "শেয়ারবাজার",
    "বাণিজ্য ঘাটতি",
    "চলতি হিসাব",
    "মজুরি",
    "কর্মসংস্থান",
    "বেকারত্ব",
]
