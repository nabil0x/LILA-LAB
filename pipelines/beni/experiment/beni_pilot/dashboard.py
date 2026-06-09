from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from config import ExperimentConfig
from data import add_economic_relevance_label, load_all_splits
from predict import BENIPredictor


st.set_page_config(page_title="BENI Dashboard", page_icon="BN", layout="wide")


@st.cache_resource
def load_predictor() -> BENIPredictor:
    return BENIPredictor()


@st.cache_data
def load_summary() -> tuple[dict[str, object], pd.DataFrame]:
    config = ExperimentConfig()
    summary_path = config.report_dir / "dataset_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    splits = load_all_splits(config)
    frame = pd.concat(
        [add_economic_relevance_label(split).assign(split=name) for name, split in splits.items()],
        ignore_index=True,
    )
    return summary, frame


def probability_table(probabilities: dict[str, float]) -> pd.DataFrame:
    if not probabilities:
        return pd.DataFrame(columns=["label", "probability"])
    return pd.DataFrame(
        [{"label": label, "probability": prob} for label, prob in probabilities.items()]
    ).sort_values("probability", ascending=False)


predictor = load_predictor()
summary, corpus = load_summary()

st.title("Bangla Economic Narrative Index Dashboard")
st.caption("Prototype classifier and narrative lens for Bangla newspaper text.")

tab_predict, tab_corpus, tab_batch, tab_about = st.tabs(
    ["Predict Text", "Corpus Signals", "Batch CSV", "Method"]
)

with tab_predict:
    default_text = (
        "বাংলাদেশ ব্যাংক ডলারের বাজার স্থিতিশীল রাখতে নতুন পদক্ষেপ নিয়েছে। "
        "রিজার্ভ চাপ, আমদানি ব্যয় এবং মূল্যস্ফীতি নিয়ে অর্থনীতিবিদরা উদ্বেগ প্রকাশ করেছেন।"
    )
    text = st.text_area("Bangla news text", value=default_text, height=180)
    prediction = predictor.predict_text(text)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Economic relevance", prediction["economic_relevance_label"])
    col2.metric("Dataset topic", prediction["topic_label"])
    col3.metric("Economic topic", prediction["narrative"]["economic_topic"]["label"])
    col4.metric("Narrative force", prediction["narrative"]["narrative_force"]["label"])

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Economic Probabilities")
        st.dataframe(probability_table(prediction["economic_probabilities"]), use_container_width=True)
        st.subheader("Narrative Target")
        st.json(prediction["narrative"]["valuation_target"])
    with col6:
        st.subheader("Topic Probabilities")
        st.dataframe(probability_table(prediction["topic_probabilities"]).head(8), use_container_width=True)
        st.subheader("Narrative Matches")
        st.json(
            {
                "topic": prediction["narrative"]["economic_topic"],
                "force": prediction["narrative"]["narrative_force"],
            }
        )

with tab_corpus:
    st.subheader("Current Training Corpus")
    col1, col2, col3 = st.columns(3)
    col1.metric("Articles", f"{len(corpus):,}")
    col2.metric("Economic weak labels", f"{int(corpus['economic_relevance'].sum()):,}")
    col3.metric("Topic classes", corpus["class_label"].nunique())

    by_split = corpus.groupby("split").size().reset_index(name="articles")
    by_topic = corpus.groupby("class_label").size().reset_index(name="articles").sort_values(
        "articles", ascending=False
    )
    by_econ_topic = (
        corpus.groupby("class_label")["economic_relevance"]
        .mean()
        .reset_index(name="economic_share")
        .sort_values("economic_share", ascending=False)
    )

    chart1, chart2 = st.columns(2)
    with chart1:
        st.bar_chart(by_topic.set_index("class_label"))
    with chart2:
        st.bar_chart(by_econ_topic.set_index("class_label"))
    st.expander("Dataset summary JSON").json(summary)

with tab_batch:
    st.subheader("Batch Predict Newspaper CSV")
    st.write("Upload a CSV with a `text` column, or set the text column name below.")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    text_column = st.text_input("Text column", value="text")
    if uploaded is not None:
        input_frame = pd.read_csv(uploaded)
        if text_column not in input_frame.columns:
            st.error(f"Column `{text_column}` was not found.")
        else:
            rows = []
            for article in input_frame[text_column].fillna(""):
                pred = predictor.predict_text(article)
                rows.append(
                    {
                        "economic_relevance": pred["economic_relevance_label"],
                        "dataset_topic": pred["topic_label"],
                        "economic_topic": pred["narrative"]["economic_topic"]["label"],
                        "narrative_force": pred["narrative"]["narrative_force"]["label"],
                        "valuation_target": pred["narrative"]["valuation_target"]["label"],
                    }
                )
            output = pd.concat([input_frame, pd.DataFrame(rows)], axis=1)
            st.dataframe(output, use_container_width=True)
            st.download_button(
                "Download predictions",
                output.to_csv(index=False).encode("utf-8"),
                file_name="beni_predictions.csv",
                mime="text/csv",
            )

with tab_about:
    st.subheader("Model Stack")
    st.write(
        "The dashboard combines TF-IDF + logistic regression models for dataset topic and weak "
        "economic relevance with explicit Bangla lexicons for economic topic, narrative force, "
        "and valuation target."
    )
    st.write(
        "This is a prototype. The next research-grade version should train on Potrika Economy, "
        "Politics, National, and International sections, then replace weak labels with 300-500 "
        "human annotations."
    )
    st.code(
        "python3 predict.py --text 'বাংলাদেশ ব্যাংক রিজার্ভ ও ডলার বাজার নিয়ে নতুন পদক্ষেপ নিয়েছে'",
        language="bash",
    )
