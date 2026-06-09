from __future__ import annotations

import json
import random
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


BANGLA_PUNCT_RE = re.compile(r"[\u0964\u0965।,;:!?\"'“”‘’()\[\]{}<>/\\|_=+*`~#@$%^&]")
SPACE_RE = re.compile(r"\s+")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def normalize_text(text: str) -> str:
    text = str(text).replace("\ufeff", " ")
    text = BANGLA_PUNCT_RE.sub(" ", text)
    text = SPACE_RE.sub(" ", text)
    return text.strip()


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def zip_outputs(output_dir: Path, prefix: str = "beni_results") -> Path:
    """Zip the output directory for easy download from Kaggle.

    Args:
        output_dir: Directory to zip (typically config.output_dir).
        prefix: Prefix for the zip filename.

    Returns:
        Path to the created zip archive.
    """
    output_dir = output_dir.resolve()
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = output_dir.parent / f"{prefix}_{timestamp}"
    shutil.make_archive(str(zip_path), "zip", output_dir)
    final_path = zip_path.with_suffix(".zip")
    size_mb = final_path.stat().st_size / 1024**2
    print(f"Results zipped: {final_path} ({size_mb:.0f} MB)", flush=True)
    return final_path
