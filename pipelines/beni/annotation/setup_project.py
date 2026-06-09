"""
Create BENI annotation project in LabelStudio and import tasks.

Run: python3 setup_project.py
Requires: label-studio server running (label-studio start -p 8080)

Imports the expanded annotation schema (economic_relevance, topic,
sentiment, narrative_force, valuation_target) and the 300-article
stratified batch with BanglaBERT pre-labels.
"""

import json
import os
from pathlib import Path

from label_studio_sdk import Client

LABEL_CONFIG_PATH = Path(__file__).parent / "label_config.xml"
BATCH_PATH = Path(__file__).parent / "exports" / "beni_300_batch_with_ml.json"
LS_URL = os.environ.get("LS_URL", "http://localhost:8080")
LS_API_KEY = os.environ.get("LS_API_KEY", "ad67813b5ba5e5ba59ad35a93a506df38e070cd9")


def main():
    label_config = LABEL_CONFIG_PATH.read_text(encoding="utf-8")
    tasks = json.loads(BATCH_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(tasks)} tasks from {BATCH_PATH}")

    client = Client(url=LS_URL, api_key=LS_API_KEY)
    client.check_connection()
    print(f"Connected to LabelStudio at {LS_URL}")

    existing = client.get_projects()
    for proj in existing:
        if proj.params["title"] == "BENI - Economic Relevance":
            print(f"Project already exists (id={proj.id}), deleting...")
            proj.delete()

    project = client.create_project(
        title="BENI - Economic Relevance",
        description=(
            "Bangla Economic Narrative Index: 300-article gold-standard annotation.\n\n"
            "Section A: Is this article economically relevant for Bangladesh?\n"
            "  - Economic: article primarily about Bangladesh's economy (GDP, inflation, trade, etc.)\n"
            "  - Not Economic: all other content\n\n"
            "Sections B-E (Economic articles only):\n"
            "  B - Macroeconomic topic (inflation, exchange rate, fiscal, trade, etc.)\n"
            "  C - Sentiment (negative / neutral / positive)\n"
            "  D - Narrative force (crisis, burden, reform, stability, uncertainty, etc.)\n"
            "  E - Valuation target (government, central bank, households, etc.)\n\n"
            "Target: Cohen's kappa >= 0.70 for Section A."
        ),
        label_config=label_config,
    )
    print(f"Created project: id={project.id}, title={project.params['title']}")

    project.import_tasks(tasks)
    print(f"Imported {len(tasks)} tasks")

    print()
    print("=" * 60)
    print("BENI Annotation Project Ready!")
    print("=" * 60)
    print(f"  URL:   {LS_URL}")
    print(f"  Tasks: {len(tasks)}")
    print(f"  Schema: economic_relevance + topic + sentiment + force + target")
    print()
    print("To start annotating:")
    print(f"  1. Open {LS_URL}")
    print(f"  2. Log in")
    print(f"  3. Click 'BENI - Economic Relevance' project")
    print(f"  4. Start annotating!")
    print()
    print("After annotation:")
    print(f"  Export → run: python3 adjudicate.py")
    print()


if __name__ == "__main__":
    main()
