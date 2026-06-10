#!/usr/bin/env python3
"""
[X]ENI — LLM Annotation Script

Multi-LLM annotation pipeline for native-language news articles.
Adapt this file for your language: configure models, prompts, and API keys.

Usage:
    python llm_annotate.py --input data/articles.jsonl \\
        --schema schemas/economic.json --output annotations/

Deliverable:
    - Annotated articles with per-field labels and confidence scores
    - Ready for adjudication and classifier training
"""

import argparse
import logging
import time
from collections import Counter
from pathlib import Path
from typing import Any

from pipelines.shared.io import ensure_dirs, read_json, read_jsonl, save_jsonl
from pipelines.shared.llm.clients import (
    call_anthropic,
    call_gemini,
    call_ollama,
    call_openai,
)
from pipelines.shared.llm.parsing import parse_llm_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Prompt templates ──────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = (
    "You are an expert annotator for news content in {language}. "
    "You are building the {pipeline_name} narrative index, which tracks "
    "how {domain} topics are discussed in {language} news media. "
    "Your task is to classify news articles across multiple dimensions.\n\n"
    "Read each article carefully and respond with a JSON object containing "
    "your annotations. Be precise and consistent."
)

USER_PROMPT_TEMPLATE = (
    "Annotate the following news article according to the {domain} schema.\n\n"
    "ARTICLE ID: {article_id}\n"
    "ARTICLE TEXT:\n{text}\n\n"
    "{fields_prompt}\n\n"
    "Respond with ONLY the JSON object, no other text."
)


# ── Schema helpers ────────────────────────────────────────────────────

def build_fields_prompt(schema: dict) -> str:
    """Build a human-readable description of annotation fields from a schema.

    Args:
        schema: Annotation schema dictionary with a ``fields`` list.

    Returns:
        Formatted string describing each field and its options.
    """
    lines = ["Respond with a JSON object containing exactly these fields:"]
    for i, field in enumerate(schema.get("fields", []), 1):
        name = field.get("name", f"field_{i}")
        description = field.get("description", "")
        options = field.get("options", [])
        lines.append(f'{i}. "{name}": {description}')
        if options:
            items = ", ".join(repr(o) for o in options)
            lines.append(f"   Options: {items}")
    return "\n".join(lines)


# ── Provider dispatch ─────────────────────────────────────────────────

def get_llm_client(provider: str) -> Any:
    """Return the callable for the requested LLM provider.

    Args:
        provider: One of ``anthropic``, ``openai``, ``gemini``, ``ollama``.

    Returns:
        The corresponding client function from ``shared.llm.clients``.

    Raises:
        ValueError: If the provider is unknown.
    """
    clients = {
        "anthropic": call_anthropic,
        "openai": call_openai,
        "gemini": call_gemini,
        "ollama": call_ollama,
    }
    if provider not in clients:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Choose from: {list(clients.keys())}"
        )
    return clients[provider]


# ── Core annotation logic ─────────────────────────────────────────────

def annotate_article(
    article: dict,
    schema: dict,
    provider: str,
    model: str,
    language: str = "your language",
    pipeline_name: str = "[X]ENI",
    max_text_length: int = 4000,
) -> dict:
    """Annotate a single article using the specified LLM provider.

    Retries up to 3 times with exponential back-off on failure.  On the
    final failure the error is captured in the result so the pipeline does
    not crash.

    Args:
        article: Article dict.  Must contain ``id`` and either ``text`` or
                 ``data.text``.
        schema: Annotation schema dictionary.
        provider: LLM provider name (``anthropic``, ``openai``, …).
        model: Model name for the chosen provider.
        language: Target language for prompt generation.
        pipeline_name: Pipeline name for prompt generation.
        max_text_length: Maximum characters of article text to send.

    Returns:
        Article dict with an ``llm_annotation`` key added.
    """
    article_id = str(article.get("id", ""))

    # Extract text from various possible formats
    text = article.get("text", "")
    if not text and "data" in article:
        text = article["data"].get("text", "")
    text = text[:max_text_length]

    if not text:
        return {
            "id": article_id,
            "llm_annotation": {"error": "No text content found in article"},
        }

    domain = schema.get("domain", "general")
    fields_prompt = build_fields_prompt(schema)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        language=language,
        pipeline_name=pipeline_name,
        domain=domain,
    )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        domain=domain,
        article_id=article_id,
        text=text,
        fields_prompt=fields_prompt,
    )

    messages = [{"role": "user", "content": user_prompt}]
    client_fn = get_llm_client(provider)

    last_error: str | None = None
    raw_response: str | None = None

    for attempt in range(3):
        try:
            raw = client_fn(
                model=model,
                system=system_prompt,
                messages=messages,
            )
            raw_response = raw
            result = parse_llm_response(raw)

            return {
                "id": article_id,
                "llm_annotation": {
                    "provider": provider,
                    "model": model,
                    **result,
                },
                "raw_response": raw,
            }
        except Exception as exc:
            last_error = str(exc)
            if attempt < 2:
                wait = 2 ** attempt
                logger.warning(
                    "Attempt %d/3 failed for article %s, retrying in %ds: %s",
                    attempt + 1, article_id, wait, exc,
                )
                time.sleep(wait)

    logger.error(
        "Failed to annotate article %s after 3 attempts: %s",
        article_id, last_error,
    )
    return {
        "id": article_id,
        "llm_annotation": {
            "provider": provider,
            "model": model,
            "error": last_error,
            "raw_response": raw_response,
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="LLM Annotation Pipeline")
    parser.add_argument(
        "--input", required=True,
        help="Input JSONL file containing articles",
    )
    parser.add_argument(
        "--schema", required=True,
        help="Annotation schema JSON file",
    )
    parser.add_argument(
        "--output", default="annotations/",
        help="Output directory for annotation results",
    )
    parser.add_argument(
        "--provider", default="anthropic",
        choices=["anthropic", "openai", "gemini", "ollama"],
        help="LLM provider to use",
    )
    parser.add_argument(
        "--model",
        default="claude-3-haiku-20240307",
        help="Model name for the chosen provider",
    )
    parser.add_argument(
        "--language", default="your language",
        help="Target language name (used in prompts)",
    )
    parser.add_argument(
        "--pipeline-name", default="[X]ENI",
        help="Pipeline name (used in prompts)",
    )
    parser.add_argument(
        "--max-articles", type=int, default=None,
        help="Limit number of articles to process (for testing)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=10,
        help="Number of articles between intermediate saves",
    )
    args = parser.parse_args()

    # Load schema and articles
    schema = read_json(Path(args.schema))
    articles = read_jsonl(Path(args.input))

    if args.max_articles:
        articles = articles[: args.max_articles]

    logger.info(
        "Loaded %d articles, schema: %s",
        len(articles), schema.get("domain", "unknown"),
    )
    logger.info("Provider: %s, Model: %s", args.provider, args.model)

    out_dir = Path(args.output)
    ensure_dirs(out_dir)

    # Annotate
    results: list[dict[str, Any]] = []
    total = len(articles)

    for i, article in enumerate(articles):
        result = annotate_article(
            article=article,
            schema=schema,
            provider=args.provider,
            model=args.model,
            language=args.language,
            pipeline_name=args.pipeline_name,
        )
        results.append(result)

        ann = result.get("llm_annotation", {})
        status = "\u2713" if "error" not in ann else "\u2717"
        logger.info(
            "  [%d/%d] %s %s",
            i + 1, total, status, str(article.get("id", ""))[:20],
        )

        # Periodic batch save
        if (i + 1) % args.batch_size == 0:
            batch_file = out_dir / f"batch_{i + 1}.jsonl"
            save_jsonl(results[-args.batch_size :], batch_file)
            logger.info("  Batch saved: %s", batch_file)

        # Rate limiting for cloud APIs
        if (i + 1) % 20 == 0 and args.provider != "ollama":
            time.sleep(1)

    # Final save
    output_file = out_dir / "annotations.jsonl"
    save_jsonl(results, output_file)
    logger.info("All annotations saved: %s", output_file)

    # Summary
    primary_field = schema.get("primary_field", "economic_relevance")
    labels = [
        r.get("llm_annotation", {}).get(primary_field)
        for r in results
    ]
    if labels:
        dist = Counter(labels)
        logger.info("Label distribution: %s", dict(dist))

    logger.info(
        "Annotation complete. %d articles annotated.",
        len(results),
    )


if __name__ == "__main__":
    main()
