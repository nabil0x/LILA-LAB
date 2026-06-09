from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from config import ExperimentConfig
from data import (
    add_economic_relevance_label,
    describe_splits,
    load_all_splits,
    load_potrika_all_categories,
    load_potrika_export,
    load_potrika_timeseries,
    save_sample,
)
from eval import evaluate_model
from models import build_tfidf_logreg
from utils import ensure_dirs, set_seed, write_json, zip_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train BENI pilot baseline models.")
    parser.add_argument("--task", choices=["topic", "economic"], default="topic")
    parser.add_argument("--max-features", type=int, default=80_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--model-type",
        choices=["tfidf", "banglabert"],
        default="tfidf",
        help="Model architecture: tfidf (fast baseline) or banglabert (fine-tuned transformer)",
    )
    parser.add_argument(
        "--data-source",
        choices=["bnlp", "potrika", "potrika-timeseries"],
        default="bnlp",
        help="Dataset source: bnlp (default, weak labels), potrika (balanced Economy articles), potrika-timeseries (raw Economy with dates)",
    )
    parser.add_argument(
        "--train-end",
        default="2018-12-31",
        help="Potrika timeseries: last date for training set (default: 2018-12-31)",
    )
    parser.add_argument(
        "--val-end",
        default="2019-12-31",
        help="Potrika timeseries: last date for validation set (default: 2019-12-31)",
    )
    parser.add_argument("--banglabert-epochs", type=int, default=3)
    parser.add_argument("--banglabert-batch-size", type=int, default=16)
    parser.add_argument("--banglabert-lr", type=float, default=2e-5)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Kaggle data directory (e.g. /kaggle/input/beni-data). Overrides potrika, macro, model, and output paths.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Zip outputs/ directory on completion (for easy download from Kaggle).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.data_dir is not None:
        # Kaggle mode: override all data paths
        dd = args.data_dir
        config = ExperimentConfig(
            seed=args.seed,
            max_features=args.max_features,
            target_task=args.task,
            potrika_train_end=args.train_end,
            potrika_val_end=args.val_end,
            banglabert_epochs=args.banglabert_epochs,
            banglabert_batch_size=args.banglabert_batch_size,
            banglabert_learning_rate=args.banglabert_lr,
            potrika_dir=dd / "potrika",
            macro_dir=dd / "macro",
            model_dir=Path("/kaggle/working/outputs/models"),  # writable: save trained models here
            output_dir=Path("/kaggle/working/outputs"),
            banglabert_dir=Path("/kaggle/working/banglabert"),  # populated by HF download at first use
        )
    else:
        config = ExperimentConfig(
            seed=args.seed,
            max_features=args.max_features,
            target_task=args.task,
            potrika_train_end=args.train_end,
            potrika_val_end=args.val_end,
            banglabert_epochs=args.banglabert_epochs,
            banglabert_batch_size=args.banglabert_batch_size,
            banglabert_learning_rate=args.banglabert_lr,
        )
    set_seed(config.seed)
    ensure_dirs(config.output_dir, config.report_dir)
    if args.data_dir is None:
        ensure_dirs(config.model_dir)  # skip in Kaggle mode (model_dir may be read-only input)

    if args.data_source == "bnlp":
        splits = load_all_splits(config)
        write_json(config.report_dir / "dataset_summary.json", describe_splits(splits))
        train = add_economic_relevance_label(splits["train"])
        dev = add_economic_relevance_label(splits["dev"])
        test = add_economic_relevance_label(splits["test"])
        save_sample(train, config.report_dir / "train_sample_with_pseudo_economic_labels.csv")
    elif args.data_source == "potrika":
        frame = load_potrika_all_categories(config.potrika_dir)
        econ_frame = load_potrika_export(config.potrika_processed)
        print(f"potrika_balanced: {len(frame)} articles across {frame['class_label'].nunique()} categories")
        print(f"potrika_economy: {len(econ_frame)} Economy articles")
        train_text = frame["text_norm"]
        train_label = frame["class_label"]
        test = dev = None
    elif args.data_source == "potrika-timeseries":
        splits = load_potrika_timeseries(config)
        train = splits["train"]
        dev = splits["val"]
        test = splits["test"]
        print(f"potrika_timeseries: train={len(train)} val={len(dev)} test={len(test)}")
        print(f"  date range: {train['publication_date'].min()} to {test['publication_date'].max()}")
        train_text = train["text_norm"]
        train_label = train["economic_relevance"]
    else:
        raise ValueError(f"Unknown data source: {args.data_source}")

    if args.model_type == "banglabert" and args.data_source in ("potrika-timeseries",):
        from banglabert import evaluate_banglabert, train_banglabert

        print(f"\nTraining BanglaBERT on {len(train)} articles...")
        result = train_banglabert(
            config,
            train_texts=train["text_norm"].tolist(),
            train_labels=train["economic_relevance"].tolist(),
            val_texts=dev["text_norm"].tolist() if dev is not None else None,
            val_labels=dev["economic_relevance"].tolist() if dev is not None else None,
            output_name=f"banglabert_{args.task}_{args.data_source}",
        )

        if test is not None and len(test) > 0:
            eval_result = evaluate_banglabert(
                config,
                test_texts=test["text_norm"].tolist(),
                test_labels=test["economic_relevance"].tolist(),
                model_name=result["output_name"],
            )
            result["test"] = eval_result

        report_path = config.report_dir / f"{args.task}_{args.data_source}_banglabert_metrics.json"
        write_json(report_path, result)
        print(f"saved_report={report_path}")

    elif args.data_source in ("bnlp", "potrika-timeseries"):
        target = "class_label" if args.task == "topic" else "economic_relevance"
        model = build_tfidf_logreg(config)
        if args.data_source == "bnlp":
            model.fit(train["text_norm"], train[target])
        else:
            model.fit(train_text, train_label)

        model_path = config.model_dir / f"{args.task}_{args.data_source}_tfidf_logreg.joblib"
        joblib.dump(model, model_path)

        report = {
            "task": args.task,
            "data_source": args.data_source,
            "model_path": str(model_path),
        }

        if args.data_source == "bnlp":
            report["assumptions"] = [
                "ASSUMPTION: TF-IDF + logistic regression is used as the first reproducible baseline.",
                "ASSUMPTION: Economic relevance labels are weak labels from a fixed keyword list, not human annotations.",
                "ASSUMPTION: This BanglaNLP dataset is a news categorization benchmark and does not contain BENI-grade sentiment labels.",
            ]
            report["dev"] = evaluate_model(model, dev["text_norm"], dev[target])
            report["test"] = evaluate_model(model, test["text_norm"], test[target])
        else:
            report["assumptions"] = [
                "ASSUMPTION: Potrika raw Economy articles are used as positive economic samples.",
                "ASSUMPTION: Date-based train/val/test split follows temporal ordering (no lookahead).",
            ]
            if dev is not None and len(dev) > 0:
                report["val"] = evaluate_model(model, dev["text_norm"], dev["economic_relevance"])
            if test is not None and len(test) > 0:
                report["test"] = evaluate_model(model, test["text_norm"], test["economic_relevance"])

        write_json(config.report_dir / f"{args.task}_{args.data_source}_metrics.json", report)
        print(f"saved_model={model_path}")
        print(f"saved_report={config.report_dir / f'{args.task}_{args.data_source}_metrics.json'}")
    else:
        print(f"potrika data loaded: {len(frame)} articles, {frame['class_label'].nunique()} categories")
        print("Use --task economic --data-source potrika-timeseries for training with dates.")

    if args.zip:
        zip_outputs(config.output_dir, f"beni_{args.task}_{args.data_source}")


if __name__ == "__main__":
    main()
