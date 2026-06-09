from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from config import ExperimentConfig
from narrative import narrative_profile
from utils import normalize_text, write_json


def _class_probabilities(model: Any, text_norm: str) -> dict[str, float]:
    if not hasattr(model, "predict_proba"):
        return {}
    probabilities = model.predict_proba([text_norm])[0]
    classes = getattr(model.named_steps.get("clf"), "classes_", []) if hasattr(model, "named_steps") else []
    return {str(label): float(prob) for label, prob in zip(classes, probabilities)}


class BENIPredictor:
    def __init__(self, config: ExperimentConfig | None = None):
        self.config = config or ExperimentConfig()
        self.topic_model = joblib.load(self.config.model_dir / "topic_tfidf_logreg.joblib")
        self.economic_model = joblib.load(self.config.model_dir / "economic_tfidf_logreg.joblib")

    def predict_text(self, text: str) -> dict[str, object]:
        text_norm = normalize_text(text)
        topic_pred = self.topic_model.predict([text_norm])[0]
        economic_pred = int(self.economic_model.predict([text_norm])[0])
        topic_probs = _class_probabilities(self.topic_model, text_norm)
        economic_probs = _class_probabilities(self.economic_model, text_norm)

        return {
            "text": text,
            "text_norm": text_norm,
            "economic_relevance": economic_pred,
            "economic_relevance_label": "economic" if economic_pred == 1 else "non_economic",
            "economic_probabilities": economic_probs,
            "topic_label": str(topic_pred),
            "topic_probabilities": topic_probs,
            "narrative": narrative_profile(text_norm),
        }

    def predict_csv(self, input_path: Path, output_path: Path, text_column: str = "text") -> pd.DataFrame:
        frame = pd.read_csv(input_path)
        if text_column not in frame.columns:
            raise ValueError(f"Missing text column '{text_column}' in {input_path}")
        predictions = [self.predict_text(text) for text in frame[text_column].fillna("")]
        out = frame.copy()
        out["beni_economic_relevance"] = [row["economic_relevance"] for row in predictions]
        out["beni_topic_label"] = [row["topic_label"] for row in predictions]
        out["beni_economic_topic"] = [row["narrative"]["economic_topic"]["label"] for row in predictions]
        out["beni_narrative_force"] = [row["narrative"]["narrative_force"]["label"] for row in predictions]
        out["beni_valuation_target"] = [row["narrative"]["valuation_target"]["label"] for row in predictions]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output_path, index=False)
        return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict BENI labels for text or CSV files.")
    parser.add_argument("--text", default=None, help="Single Bangla news text to classify.")
    parser.add_argument("--input-csv", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=Path("../outputs/reports/beni_predictions.csv"))
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--output-json", type=Path, default=Path("../outputs/reports/latest_text_prediction.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    predictor = BENIPredictor()
    if args.input_csv:
        out = predictor.predict_csv(args.input_csv, args.output_csv, args.text_column)
        print(f"rows={len(out)}")
        print(f"output_csv={args.output_csv}")
        return
    if not args.text:
        raise SystemExit("Provide --text or --input-csv")
    prediction = predictor.predict_text(args.text)
    write_json(args.output_json, prediction)
    print(f"label={prediction['economic_relevance_label']}")
    print(f"topic={prediction['topic_label']}")
    print(f"economic_topic={prediction['narrative']['economic_topic']['label']}")
    print(f"narrative_force={prediction['narrative']['narrative_force']['label']}")
    print(f"valuation_target={prediction['narrative']['valuation_target']['label']}")
    print(f"output_json={args.output_json}")


if __name__ == "__main__":
    main()
