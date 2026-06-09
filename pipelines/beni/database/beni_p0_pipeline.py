from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "database" / "beni_v0_1.sqlite"
DEFAULT_ANNOTATIONS = ROOT / "annotation" / "exports" / "llm_assisted_300_annotations.jsonl"
DEFAULT_CORPUS_DIR = ROOT / "Bangla_News_Database"
DEFAULT_MACRO_DIR = ROOT / "data" / "raw" / "macro"
DEFAULT_OUTPUT_DIR = ROOT / "database" / "outputs"

ECONOMIC_KEYWORDS = {
    "অর্থনীতি",
    "অর্থনৈতিক",
    "মূল্যস্ফীতি",
    "মুদ্রাস্ফীতি",
    "দ্রব্যমূল্য",
    "ডলার",
    "রিজার্ভ",
    "বাংলাদেশ ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "কেন্দ্রীয় ব্যাংক",
    "বিনিময় হার",
    "বিনিময় হার",
    "সুদের হার",
    "ব্যাংক",
    "ঋণ",
    "আমানত",
    "বাজেট",
    "কর",
    "ভ্যাট",
    "শুল্ক",
    "রাজস্ব",
    "ভর্তুকি",
    "ঘাটতি",
    "রপ্তানি",
    "আমদানি",
    "বাণিজ্য",
    "জিডিপি",
    "প্রবৃদ্ধি",
    "বিনিয়োগ",
    "বিনিয়োগ",
    "রেমিট্যান্স",
    "পুঁজিবাজার",
    "শেয়ারবাজার",
    "শেয়ারবাজার",
    "কর্মসংস্থান",
    "বেকারত্ব",
    "মজুরি",
    "গার্মেন্ট",
}

TOPIC_TERMS = {
    "inflation": ["মূল্যস্ফীতি", "মুদ্রাস্ফীতি", "দাম", "মূল্য", "দ্রব্যমূল্য"],
    "exchange_rate": ["ডলার", "টাকা", "বিনিময় হার", "বিনিময় হার"],
    "banking": ["ব্যাংক", "ঋণ", "আমানত", "সুদ", "তারল্য"],
    "fiscal_policy": ["বাজেট", "কর", "ভ্যাট", "শুল্ক", "রাজস্ব", "ভর্তুকি"],
    "trade": ["রপ্তানি", "আমদানি", "বাণিজ্য", "এলসি", "বন্দর"],
}

PRESSURE_TERMS = ["সংকট", "চাপ", "ঝুঁকি", "ঘাটতি", "দুর্ভোগ", "অনিশ্চয়তা", "অনিশ্চয়তা", "আশঙ্কা"]
POSITIVE_TERMS = ["স্থিতিশীল", "স্বস্তি", "উন্নতি", "প্রবৃদ্ধি", "সম্ভাবনা", "পুনরুদ্ধার"]

BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
BANGLA_MONTHS = {
    "জানুয়ারি": 1,
    "জানুয়ারি": 1,
    "ফেব্রুয়ারি": 2,
    "ফেব্রুয়ারি": 2,
    "মার্চ": 3,
    "এপ্রিল": 4,
    "মে": 5,
    "জুন": 6,
    "জুলাই": 7,
    "আগস্ট": 8,
    "সেপ্টেম্বর": 9,
    "অক্টোবর": 10,
    "নভেম্বর": 11,
    "ডিসেম্বর": 12,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_hash(text: str) -> str:
    return hashlib.sha1(normalize(text).encode("utf-8")).hexdigest()


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_file TEXT,
    language TEXT DEFAULT 'bn'
);

CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    source_id INTEGER REFERENCES sources(source_id),
    title TEXT,
    body_text TEXT NOT NULL,
    publication_raw TEXT,
    publication_date TEXT,
    year_month TEXT,
    category TEXT,
    raw_path TEXT,
    raw_line INTEGER,
    text_hash TEXT NOT NULL,
    duplicate_group_id TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    UNIQUE(source_id, raw_line)
);

CREATE INDEX IF NOT EXISTS idx_articles_month ON articles(year_month);
CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(text_hash);

CREATE TABLE IF NOT EXISTS annotations (
    annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL REFERENCES articles(article_id),
    dataset_version TEXT NOT NULL,
    final_label TEXT NOT NULL CHECK(final_label IN ('Economic', 'Not Economic')),
    confidence INTEGER,
    difficulty TEXT,
    annotation_status TEXT NOT NULL CHECK(annotation_status IN ('human_verified', 'llm_assisted', 'needs_review')),
    annotation_method TEXT,
    annotator_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(article_id, dataset_version)
);

CREATE TABLE IF NOT EXISTS model_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL REFERENCES articles(article_id),
    model_version TEXT NOT NULL,
    predicted_label TEXT NOT NULL CHECK(predicted_label IN ('Economic', 'Not Economic')),
    economic_probability REAL NOT NULL,
    predicted_at TEXT NOT NULL,
    UNIQUE(article_id, model_version)
);

CREATE TABLE IF NOT EXISTS index_values (
    index_id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_version TEXT NOT NULL,
    year_month TEXT NOT NULL,
    n_articles INTEGER NOT NULL,
    n_economic INTEGER NOT NULL,
    economic_share REAL NOT NULL,
    mean_economic_probability REAL NOT NULL,
    pressure_score REAL NOT NULL,
    inflation_share REAL NOT NULL,
    exchange_rate_share REAL NOT NULL,
    banking_share REAL NOT NULL,
    fiscal_policy_share REAL NOT NULL,
    trade_share REAL NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(index_version, year_month)
);

CREATE TABLE IF NOT EXISTS macro_indicators (
    indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,
    frequency TEXT NOT NULL,
    period TEXT NOT NULL,
    value REAL NOT NULL,
    source_file TEXT,
    UNIQUE(indicator_name, frequency, period)
);
"""


def init_db(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Initialized schema: {args.db}")


def parse_bangla_date(raw: str) -> str | None:
    raw = normalize(raw).translate(BANGLA_DIGITS)
    for month_name, month in BANGLA_MONTHS.items():
        if month_name not in raw:
            continue
        match = re.search(rf"(\d{{1,2}})\s+{re.escape(month_name)}\s+(\d{{4}})", raw)
        if not match:
            continue
        day = int(match.group(1))
        year = int(match.group(2))
        try:
            return datetime(year, month, day).date().isoformat()
        except ValueError:
            return None
    iso_match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", raw)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        try:
            return datetime(year, month, day).date().isoformat()
        except ValueError:
            return None
    return None


def get_source_id(conn: sqlite3.Connection, source_name: str, source_file: str) -> int:
    conn.execute(
        "INSERT OR IGNORE INTO sources(source_name, source_file) VALUES (?, ?)",
        (source_name, source_file),
    )
    row = conn.execute("SELECT source_id FROM sources WHERE source_name = ?", (source_name,)).fetchone()
    return int(row[0])


def upsert_article(
    conn: sqlite3.Connection,
    *,
    article_id: str,
    source_name: str,
    source_file: str,
    title: str,
    body_text: str,
    publication_raw: str,
    category: str,
    raw_path: str,
    raw_line: int | None,
) -> None:
    full_text = normalize(f"{title}\n\n{body_text}")
    digest = text_hash(full_text)
    publication_date = parse_bangla_date(publication_raw)
    year_month = publication_date[:7] if publication_date else None
    source_id = get_source_id(conn, source_name, source_file)
    conn.execute(
        """
        INSERT OR IGNORE INTO articles(
            article_id, source_id, title, body_text, publication_raw, publication_date,
            year_month, category, raw_path, raw_line, text_hash, duplicate_group_id, imported_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article_id,
            source_id,
            title,
            body_text,
            publication_raw,
            publication_date,
            year_month,
            category,
            raw_path,
            raw_line,
            digest,
            digest,
            now_iso(),
        ),
    )


def freeze_annotations(args: argparse.Namespace) -> None:
    rows = [json.loads(line) for line in args.annotations.read_text(encoding="utf-8").splitlines() if line]
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    frozen_path = out_dir / "beni_v0_1_annotations_locked.jsonl"
    review_path = out_dir / "beni_v0_1_review_queue.csv"

    frozen = []
    for row in rows:
        status = "needs_review" if row.get("confidence", 0) < 3 or row.get("difficulty") == "Borderline" else "llm_assisted"
        locked = {
            "dataset_version": "BENI_v0.1",
            "article_id": row["id"],
            "title": row.get("title", ""),
            "text": row["text"],
            "source": row.get("source", ""),
            "source_file": row.get("source_file", ""),
            "source_line": row.get("source_line"),
            "category": row.get("category", ""),
            "publication_raw": row.get("time", ""),
            "final_label": row["economic_relevance"],
            "confidence": row.get("confidence"),
            "difficulty": row.get("difficulty"),
            "annotation_status": status,
            "annotation_method": row.get("annotation_method", "llm_assisted"),
            "locked_at": now_iso(),
        }
        frozen.append(locked)

    frozen_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in frozen) + "\n",
        encoding="utf-8",
    )
    review_rows = [
        {
            "article_id": row["article_id"],
            "final_label": row["final_label"],
            "confidence": row["confidence"],
            "difficulty": row["difficulty"],
            "category": row["category"],
            "title": row["title"],
            "text_preview": row["text"][:300],
        }
        for row in frozen
        if row["annotation_status"] == "needs_review"
    ]
    pd.DataFrame(review_rows).to_csv(review_path, index=False)
    print(f"Locked annotations: {frozen_path}")
    print(f"Review queue: {review_path} ({len(review_rows)} rows)")
    print(f"Status counts: {dict(Counter(row['annotation_status'] for row in frozen))}")


def import_annotations(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    conn.executescript(SCHEMA)
    rows = [json.loads(line) for line in args.locked_annotations.read_text(encoding="utf-8").splitlines() if line]
    for row in rows:
        upsert_article(
            conn,
            article_id=row["article_id"],
            source_name=row["source"],
            source_file=row["source_file"],
            title=row["title"],
            body_text=row["text"],
            publication_raw=row.get("publication_raw", ""),
            category=row.get("category", ""),
            raw_path=row.get("source_file", ""),
            raw_line=row.get("source_line"),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO annotations(
                article_id, dataset_version, final_label, confidence, difficulty,
                annotation_status, annotation_method, annotator_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["article_id"],
                row["dataset_version"],
                row["final_label"],
                row.get("confidence"),
                row.get("difficulty"),
                row["annotation_status"],
                row.get("annotation_method"),
                "BENI_pipeline",
                now_iso(),
            ),
        )
    conn.commit()
    conn.close()
    print(f"Imported {len(rows)} locked annotations into {args.db}")


def import_corpus(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    conn.executescript(SCHEMA)
    n = 0
    for path in sorted(args.corpus_dir.glob("*.jsonl")):
        source_name = path.stem
        for line_no, line in enumerate(path.open(encoding="utf-8"), start=1):
            if args.max_articles and n >= args.max_articles:
                conn.commit()
                conn.close()
                print(f"Imported {n} corpus articles into {args.db}")
                return
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = normalize(str(raw.get("Title") or ""))
            body = normalize(str(raw.get("Content") or raw.get("Meta") or ""))
            if not body:
                continue
            article_id = f"corpus_{source_name}_{line_no}_{hashlib.sha1(f'{source_name}:{line_no}:{title}'.encode('utf-8')).hexdigest()[:12]}"
            upsert_article(
                conn,
                article_id=article_id,
                source_name=source_name,
                source_file=path.name,
                title=title,
                body_text=body,
                publication_raw=normalize(str(raw.get("Time") or "")),
                category=normalize(str(raw.get("Category") or "")),
                raw_path=str(path),
                raw_line=line_no,
            )
            n += 1
        conn.commit()
    conn.close()
    print(f"Imported {n} corpus articles into {args.db}")


def keyword_predict(texts: list[str]) -> list[int]:
    return [int(any(term in text for term in ECONOMIC_KEYWORDS)) for text in texts]


def train_filter(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    query = """
        SELECT a.article_id, a.title, a.body_text, an.final_label
        FROM annotations an
        JOIN articles a ON a.article_id = an.article_id
        WHERE an.dataset_version = ?
    """
    df = pd.read_sql_query(query, conn, params=(args.dataset_version,))
    conn.close()
    if len(df) < 20:
        raise ValueError(f"Need more labelled rows; found {len(df)}")

    df["text"] = (df["title"].fillna("") + " " + df["body_text"].fillna("")).map(normalize)
    y = (df["final_label"] == "Economic").astype(int)
    train_x, test_x, train_y, test_y = train_test_split(
        df["text"], y, test_size=args.test_size, random_state=42, stratify=y
    )

    kw_pred = keyword_predict(test_x.tolist())
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", ngram_range=(1, 2), min_df=1, max_features=30000)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )
    pipeline.fit(train_x, train_y)
    pred = pipeline.predict(test_x)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_version = f"beni_v0_1_tfidf_logreg_{datetime.now().strftime('%Y%m%d')}"
    model_path = args.output_dir / f"{model_version}.joblib"
    joblib.dump(pipeline, model_path)

    def metrics(name: str, values: list[int] | Any) -> dict[str, Any]:
        return {
            "model": name,
            "accuracy": accuracy_score(test_y, values),
            "precision": precision_score(test_y, values, zero_division=0),
            "recall": recall_score(test_y, values, zero_division=0),
            "f1": f1_score(test_y, values, zero_division=0),
            "confusion_matrix": confusion_matrix(test_y, values).tolist(),
        }

    report = {
        "dataset_version": args.dataset_version,
        "n_rows": int(len(df)),
        "train_rows": int(len(train_x)),
        "test_rows": int(len(test_x)),
        "label_counts": {str(k): int(v) for k, v in Counter(df["final_label"]).items()},
        "model_version": model_version,
        "model_path": str(model_path),
        "metrics": [metrics("keyword_baseline", kw_pred), metrics("tfidf_logreg", pred)],
    }
    report_path = args.output_dir / "beni_v0_1_filter_metrics.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def predict_corpus(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    model = joblib.load(args.model_path)
    model_version = args.model_path.stem
    offset = 0
    total = 0
    while True:
        df = pd.read_sql_query(
            """
            SELECT article_id, title, body_text FROM articles
            ORDER BY article_id
            LIMIT ? OFFSET ?
            """,
            conn,
            params=(args.batch_size, offset),
        )
        if df.empty:
            break
        texts = (df["title"].fillna("") + " " + df["body_text"].fillna("")).map(normalize)
        probs = model.predict_proba(texts)[:, 1]
        for article_id, prob in zip(df["article_id"], probs):
            conn.execute(
                """
                INSERT OR REPLACE INTO model_predictions(
                    article_id, model_version, predicted_label, economic_probability, predicted_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (article_id, model_version, "Economic" if prob >= 0.5 else "Not Economic", float(prob), now_iso()),
            )
        conn.commit()
        total += len(df)
        offset += args.batch_size
    conn.close()
    print(f"Stored predictions for {total} articles with {model_version}")


def count_terms(text: str, terms: list[str]) -> int:
    tokens = set(re.findall(r"[\u0980-\u09FF]+", text))
    count = 0
    for term in terms:
        if " " in term or len(term) > 4:
            count += int(term in text)
        else:
            count += int(term in tokens)
    return count


def build_index(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    df = pd.read_sql_query(
        """
        SELECT a.article_id, a.year_month, a.title, a.body_text, p.economic_probability, p.predicted_label
        FROM articles a
        JOIN model_predictions p ON p.article_id = a.article_id
        WHERE p.model_version = ? AND a.year_month IS NOT NULL
        """,
        conn,
        params=(args.model_version,),
    )
    if df.empty:
        raise ValueError("No dated predictions found for index construction")
    df["text"] = (df["title"].fillna("") + " " + df["body_text"].fillna("")).map(normalize)
    df["economic_pred"] = (df["predicted_label"] == "Economic").astype(int)
    econ = df[df["economic_pred"] == 1].copy()
    for topic, terms in TOPIC_TERMS.items():
        econ[f"{topic}_hit"] = econ["text"].map(lambda text, t=terms: int(count_terms(text, t) > 0))
    econ["pressure_raw"] = econ["text"].map(lambda text: count_terms(text, PRESSURE_TERMS) - count_terms(text, POSITIVE_TERMS))

    base = df.groupby("year_month").agg(
        n_articles=("article_id", "count"),
        n_economic=("economic_pred", "sum"),
        mean_economic_probability=("economic_probability", "mean"),
    )
    if not econ.empty:
        topic_agg = econ.groupby("year_month").agg(
            pressure_score=("pressure_raw", "mean"),
            inflation_share=("inflation_hit", "mean"),
            exchange_rate_share=("exchange_rate_hit", "mean"),
            banking_share=("banking_hit", "mean"),
            fiscal_policy_share=("fiscal_policy_hit", "mean"),
            trade_share=("trade_hit", "mean"),
        )
        monthly = base.join(topic_agg, how="left")
    else:
        monthly = base
    monthly = monthly.fillna(0).reset_index()
    monthly["economic_share"] = monthly["n_economic"] / monthly["n_articles"]
    created_at = now_iso()
    for row in monthly.to_dict(orient="records"):
        conn.execute(
            """
            INSERT OR REPLACE INTO index_values(
                index_version, year_month, n_articles, n_economic, economic_share,
                mean_economic_probability, pressure_score, inflation_share,
                exchange_rate_share, banking_share, fiscal_policy_share, trade_share, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.index_version,
                row["year_month"],
                int(row["n_articles"]),
                int(row["n_economic"]),
                float(row["economic_share"]),
                float(row["mean_economic_probability"]),
                float(row["pressure_score"]),
                float(row["inflation_share"]),
                float(row["exchange_rate_share"]),
                float(row["banking_share"]),
                float(row["fiscal_policy_share"]),
                float(row["trade_share"]),
                created_at,
            ),
        )
    conn.commit()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / f"{args.index_version}_monthly_index.csv"
    monthly.to_csv(out_path, index=False)
    conn.close()
    print(f"Built monthly index: {out_path} ({len(monthly)} months)")


def _parse_imf_period(period: str) -> str:
    return period.replace("-M", "-")


def import_macro(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    conn.executescript(SCHEMA)
    files = {
        "fx_bis": ("monthly", args.macro_dir / "fx_bdt_usd_bis_eop_monthly.csv", "TIME_PERIOD", "OBS_VALUE"),
        "cpi": ("monthly", args.macro_dir / "cpi_imf_bgd_index_monthly.csv", "TIME_PERIOD", "OBS_VALUE"),
        "fx_imf": ("monthly", args.macro_dir / "fx_bdt_usd_imf_eop_monthly.csv", "TIME_PERIOD", "OBS_VALUE"),
    }
    n = 0
    for name, (freq, path, period_col, value_col) in files.items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for _, row in df.dropna(subset=[period_col, value_col]).iterrows():
            period = str(row[period_col])
            if "-M" in period:
                period = _parse_imf_period(period)
            conn.execute(
                "INSERT OR REPLACE INTO macro_indicators(indicator_name, frequency, period, value, source_file) VALUES (?, ?, ?, ?, ?)",
                (name, freq, period[:7], float(row[value_col]), path.name),
            )
            n += 1
    reserves = args.macro_dir / "reserves_wb_annual.csv"
    if reserves.exists():
        df = pd.read_csv(reserves)
        for _, row in df.dropna(subset=["year", "reserves_usd"]).iterrows():
            conn.execute(
                "INSERT OR REPLACE INTO macro_indicators(indicator_name, frequency, period, value, source_file) VALUES (?, ?, ?, ?, ?)",
                ("reserves_usd", "annual", str(int(row["year"])), float(row["reserves_usd"]), reserves.name),
            )
            n += 1
    conn.commit()
    conn.close()
    print(f"Imported {n} macro observations")


def validate_index(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    idx = pd.read_sql_query(
        "SELECT * FROM index_values WHERE index_version = ? ORDER BY year_month",
        conn,
        params=(args.index_version,),
    )
    macro = pd.read_sql_query("SELECT * FROM macro_indicators WHERE frequency = 'monthly'", conn)
    conn.close()
    rows = []
    for indicator in sorted(macro["indicator_name"].unique()):
        m = macro[macro["indicator_name"] == indicator][["period", "value"]].rename(columns={"period": "year_month"})
        merged = idx.merge(m, on="year_month", how="inner")
        for x_col in ["economic_share", "mean_economic_probability", "pressure_score"]:
            pair = merged[[x_col, "value"]].dropna()
            if len(pair) < 5:
                continue
            pr, pp = pearsonr(pair[x_col], pair["value"])
            sr, sp = spearmanr(pair[x_col], pair["value"])
            rows.append(
                {
                    "index_version": args.index_version,
                    "frequency": "monthly_level",
                    "x": x_col,
                    "y": indicator,
                    "n": len(pair),
                    "pearson_r": pr,
                    "pearson_p": pp,
                    "spearman_r": sr,
                    "spearman_p": sp,
                }
            )
            diffed = pair.diff().dropna()
            if len(diffed) >= 5:
                pr, pp = pearsonr(diffed[x_col], diffed["value"])
                sr, sp = spearmanr(diffed[x_col], diffed["value"])
                rows.append(
                    {
                        "index_version": args.index_version,
                        "frequency": "monthly_d1",
                        "x": x_col,
                        "y": indicator,
                        "n": len(diffed),
                        "pearson_r": pr,
                        "pearson_p": pp,
                        "spearman_r": sr,
                        "spearman_p": sp,
                    }
                )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(rows)
    out_path = args.output_dir / f"{args.index_version}_macro_correlations.csv"
    out.to_csv(out_path, index=False)
    print(f"Validation correlations: {out_path} ({len(out)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description="BENI P0 database and index pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_db(p: argparse.ArgumentParser) -> None:
        p.add_argument("--db", type=Path, default=DEFAULT_DB)

    p = sub.add_parser("init-db")
    add_db(p)
    p.set_defaults(func=init_db)

    p = sub.add_parser("freeze-annotations")
    p.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    p.add_argument("--output-dir", type=Path, default=ROOT / "annotation" / "exports")
    p.set_defaults(func=freeze_annotations)

    p = sub.add_parser("import-annotations")
    add_db(p)
    p.add_argument("--locked-annotations", type=Path, default=ROOT / "annotation" / "exports" / "beni_v0_1_annotations_locked.jsonl")
    p.set_defaults(func=import_annotations)

    p = sub.add_parser("import-corpus")
    add_db(p)
    p.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR)
    p.add_argument("--max-articles", type=int, default=None)
    p.set_defaults(func=import_corpus)

    p = sub.add_parser("train-filter")
    add_db(p)
    p.add_argument("--dataset-version", default="BENI_v0.1")
    p.add_argument("--test-size", type=float, default=0.25)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.set_defaults(func=train_filter)

    p = sub.add_parser("predict-corpus")
    add_db(p)
    p.add_argument("--model-path", type=Path, required=True)
    p.add_argument("--batch-size", type=int, default=5000)
    p.set_defaults(func=predict_corpus)

    p = sub.add_parser("build-index")
    add_db(p)
    p.add_argument("--model-version", required=True)
    p.add_argument("--index-version", default="BENI_v0_1_monthly")
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.set_defaults(func=build_index)

    p = sub.add_parser("import-macro")
    add_db(p)
    p.add_argument("--macro-dir", type=Path, default=DEFAULT_MACRO_DIR)
    p.set_defaults(func=import_macro)

    p = sub.add_parser("validate-index")
    add_db(p)
    p.add_argument("--index-version", default="BENI_v0_1_monthly")
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.set_defaults(func=validate_index)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
