"""Unified LLM API clients.

Supports Anthropic, OpenAI, Google Gemini, and Ollama (via OpenAI-compatible API).
All functions are language-agnostic — prompts stay in the pipeline code.
"""

import json
import os
from typing import Any


def call_anthropic(
    model: str,
    system: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 500,
    temperature: float = 0.0,
    api_key: str | None = None,
) -> str:
    """Call Anthropic Claude API.

    Args:
        model: Model name (e.g., 'claude-3-haiku-20240307').
        system: System prompt.
        messages: List of {'role': 'user'|'assistant', 'content': '...'} dicts.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature (0.0 = deterministic).
        api_key: API key (defaults to ANTHROPIC_API_KEY env var).

    Returns:
        Response text.
    """
    import anthropic

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set. Pass api_key or set the env var.")

    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        temperature=temperature,
    )
    return response.content[0].text


def call_openai(
    model: str,
    system: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 500,
    temperature: float = 0.0,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """Call OpenAI API (or compatible API like Ollama).

    Args:
        model: Model name (e.g., 'gpt-4o', 'llama3').
        system: System prompt.
        messages: List of {'role': 'user'|'assistant', 'content': '...'} dicts.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature (0.0 = deterministic).
        api_key: API key (defaults to OPENAI_API_KEY env var).
        base_url: Custom base URL (for Ollama or other compatible APIs).

    Returns:
        Response text.
    """
    import openai

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key and not base_url:
        raise ValueError("OPENAI_API_KEY not set. Pass api_key or set the env var.")

    kwargs: dict[str, Any] = {}
    if base_url:
        kwargs["base_url"] = base_url
    if key:
        kwargs["api_key"] = key

    client = openai.OpenAI(**kwargs)

    full_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def call_gemini(
    model: str,
    system: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 500,
    temperature: float = 0.0,
    api_key: str | None = None,
) -> str:
    """Call Google Gemini API.

    Args:
        model: Model name (e.g., 'gemini-1.5-flash').
        system: System prompt.
        messages: List of {'role': 'user'|'assistant', 'content': '...'} dicts.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature (0.0 = deterministic).
        api_key: API key (defaults to GEMINI_API_KEY env var).

    Returns:
        Response text.
    """
    import google.generativeai as genai

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set. Pass api_key or set the env var.")

    genai.configure(api_key=key)
    gen_config = genai.types.GenerationConfig(
        max_output_tokens=max_tokens,
        temperature=temperature,
    )

    # Gemini uses a single prompt, not messages array
    last_user_msg = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "",
    )

    model_instance = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config=gen_config,
    )
    response = model_instance.generate_content(last_user_msg)
    return response.text


def call_ollama(
    model: str,
    system: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 600,
    temperature: float = 0.0,
    base_url: str | None = None,
) -> str:
    """Call Ollama local model via OpenAI-compatible API.

    Args:
        model: Model name (e.g., 'llama3', 'mistral').
        system: System prompt.
        messages: List of {'role': 'user'|'assistant', 'content': '...'} dicts.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature (0.0 = deterministic).
        base_url: Ollama API URL (defaults to OLLAMA_HOST env var or localhost:11434).

    Returns:
        Response text.
    """
    url = base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434/v1")
    return call_openai(
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        api_key="ollama",
        base_url=url,
    )
