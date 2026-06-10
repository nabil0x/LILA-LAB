"""Base experiment configuration.

Reusable dataclass for ML experiment settings.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BaseExperimentConfig:
    """Base configuration for XENI pipeline experiments.

    Subclass this and add pipeline-specific fields.
    """

    # Reproducibility
    seed: int = 42

    # TF-IDF hyperparameters
    max_features: int = 80_000
    min_df: int = 2
    ngram_range: tuple[int, int] = (1, 2)
    max_iter: int = 1_000

    # Data splits
    test_size: float = 0.2
    val_size: float = 0.1

    # Paths (override in subclass)
    output_dir: Path = Path("outputs")
    model_dir: Path = Path("outputs/models")
    report_dir: Path = Path("outputs/reports")
    data_dir: Path = Path("data")
