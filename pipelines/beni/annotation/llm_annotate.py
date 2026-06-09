"""
LLM-as-Annotator pipeline for BENI 300-article batch.

Annotates articles using OpenAI, Anthropic, or Google Gemini API with the
full BENI schema: economic_relevance, topic, sentiment, narrative_force,
valuation_target, confidence, difficulty.

Produces two runs for self-consistency measurement.

Usage:
    # Set your API key
    export ANTHROPIC_API_KEY="sk-..."
    # or export OPENAI_API_KEY="sk-..."
    # or export GEMINI_API_KEY="..."

    # Run annotation (pass 1)
    python3 llm_annotate.py --provider anthropic --model claude-sonnet-4-20250514 \
        --input exports/beni_300_batch.json \
        --output exports/llm_pass1.json \
        --pass-id 1

    # Run annotation (pass 2 — same articles, different seed)
    python3 llm_annotate.py --provider anthropic --model claude-sonnet-4-20250514 \
        --input exports/beni_300_batch.json \
        --output exports/llm_pass2.json \
        --pass-id 2 --seed 2024

    # Analyze agreement
    python3 analyze_llm_annotations.py \
        --pass1 exports/llm_pass1.json \
        --pass2 exports/llm_pass2.json \
        --tfidf-labels exports/beni_300_batch_with_ml.json \
        --output exports/llm_report.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

# ── Supported providers ──────────────────────────────────────────────

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Prompt template ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert annotator for economic news content in Bengali. You are building the Bangla Economic Narrative Index (BENI), the first Bengali-language economic sentiment index for Bangladesh. Your task is to classify Bengali news articles across multiple dimensions.

Read each article carefully and respond with a JSON object containing your annotations. Be precise and consistent."""

USER_PROMPT_TEMPLATE = """Annotate the following Bengali news article according to the BENI schema.

ARTICLE ID: {article_id}
ARTICLE TEXT:
{text}

Respond with a JSON object containing exactly these fields:

1. "economic_relevance": Either "Economic" or "Not Economic"
   - Economic = article's PRIMARY subject is Bangladesh's economy: GDP, inflation, trade, fiscal policy, banking, forex, agriculture, industry, prices, employment, remittances, economic policy
   - Not Economic = all other content (politics without economic framing, crime, sports, entertainment, culture, general international news, human interest, mythology, religion)

2. "confidence": Integer 1-3
   - 1 = Guessing, 2 = Fairly sure, 3 = Certain

3. "difficulty": "Clear-cut" or "Borderline" (only if economic_relevance = "Economic")

4. "economic_topic": One of these values (only if economic_relevance = "Economic"):
   "inflation_prices", "exchange_rate_reserves", "monetary_banking", "fiscal_budget",
   "trade_external", "employment_wages", "agriculture_food", "industry_investment",
   "remittances", "energy_imports", "general_economy", "other"

5. "sentiment": "negative", "neutral", or "positive" (only if Economic)
   - Rate the ECONOMIC outlook conveyed, not the political tone

6. "narrative_force": One of (only if Economic):
   "crisis_warning", "burden_hardship", "blame_criticism", "reform_solution",
   "stability_confidence", "uncertainty_concern", "resilience_opportunity", "neutral_reporting"

7. "valuation_target": One of (only if Economic):
   "government", "central_bank", "banks_financial", "businesses",
   "households", "global_economy", "market_actors", "unnamed_system"

8. "notes": A brief string explaining your reasoning (optional)

IMPORTANT RULES:
- "কর" (tax) in Bengali is ambiguous — it can mean "tax" (economic) or be a verb suffix / part of compound words (not economic). Read the FULL context to determine which.
- Articles about INDIAN politics (Kolkata, West Bengal) set in India are generally "Not Economic" for BENI since the index targets Bangladesh.
- An article about "rising prices" or "inflation" IS economic even if it mentions politicians.
- An article about a political rally or crime is NOT economic even if it briefly mentions the economy.
- If the article text is truncated, annotate based on what you can see. Note the truncation in "notes".

Respond with ONLY the JSON object, no other text."""


def call_anthropic(model: str, system: str, messages: list[dict], max_tokens: int = 500) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    resp = client.messages.create(
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return resp.content[0].text


def call_openai(model: str, system: str, messages: list[dict], max_tokens: int = 500) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return resp.choices[0].message.content


def call_gemini(model: str, system: str, messages: list[dict], max_tokens: int = 500) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config={"temperature": 0.0, "max_output_tokens": max_tokens},
    )
    prompt = messages[-1]["content"] if messages else ""
    resp = gemini_model.generate_content(prompt)
    return resp.text


def parse_llm_response(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response (handles markdown fences)."""
    # Strip markdown code fences
    text = text.strip()
    if text.startswith("```"):
        # Find the first { or [
        start = text.find("{")
        if start >= 0:
            text = text[start:]
        end = text.rfind("}")
        if end >= 0:
            text = text[: end + 1]
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def annotate_article(
    provider: str,
    model: str,
    article: dict[str, Any],
    seed: int = 42,
) -> dict[str, Any]:
    """Annotate a single article using the specified LLM provider."""
    text = article["data"]["text"][:4000]  # Limit to 4K chars
    user_msg = USER_PROMPT_TEMPLATE.format(
        article_id=article["id"],
        text=text,
    )

    messages = [{"role": "user", "content": user_msg}]

    for attempt in range(3):
        try:
            if provider == "anthropic":
                raw = call_anthropic(model, SYSTEM_PROMPT, messages)
            elif provider == "openai":
                raw = call_openai(model, SYSTEM_PROMPT, messages)
            elif provider == "gemini":
                raw = call_gemini(model, SYSTEM_PROMPT, messages)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            result = parse_llm_response(raw)
            return {
                "id": article["id"],
                "data": article["data"],
                "llm_annotation": {
                    "provider": provider,
                    "model": model,
                    "seed": seed,
                    **result,
                },
                "raw_response": raw,
            }
        except json.JSONDecodeError as e:
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": provider,
                        "model": model,
                        "seed": seed,
                        "error": f"JSON parse failed: {e}",
                        "raw": raw,
                    },
                }
            time.sleep(1)
        except Exception as e:
            if attempt == 2:
                return {
                    "id": article["id"],
                    "data": article["data"],
                    "llm_annotation": {
                        "provider": provider,
                        "model": model,
                        "seed": seed,
                        "error": str(e),
                    },
                }
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description="LLM annotator for BENI")
    parser.add_argument("--provider", choices=["anthropic", "openai", "gemini"], required=True)
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pass-id", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-articles", type=int, default=None,
                        help="For testing: limit articles processed")
    args = parser.parse_args()

    # Load articles
    articles = json.loads(args.input.read_text(encoding="utf-8"))
    if args.max_articles:
        articles = articles[: args.max_articles]
    print(f"Loaded {len(articles)} articles")

    # Shuffle with seed for pass 2 (different ordering)
    random.seed(args.seed)
    indices = list(range(len(articles)))
    random.shuffle(indices)

    results = []
    total = len(articles)
    api_calls = 0

    for i, idx in enumerate(indices):
        article = articles[idx]
        result = annotate_article(args.provider, args.model, article, args.seed)
        results.append(result)
        api_calls += 1

        ann = result.get("llm_annotation", {})
        label = ann.get("economic_relevance", "ERROR")
        status = "✓" if label in ("Economic", "Not Economic") else "✗"
        print(f"  [{i+1}/{total}] {status} {article['id'][:20]:<20s} → {label}")

        # Rate limiting
        if api_calls % 20 == 0:
            time.sleep(2)

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Summary
    labels = [r.get("llm_annotation", {}).get("economic_relevance") for r in results]
    econ = sum(1 for l in labels if l == "Economic")
    not_econ = sum(1 for l in labels if l == "Not Economic")
    errors = sum(1 for l in labels if l not in ("Economic", "Not Economic"))
    print(f"\nDone. {econ} Economic, {not_econ} Not Economic, {errors} errors → {args.output}")


if __name__ == "__main__":
    main()
