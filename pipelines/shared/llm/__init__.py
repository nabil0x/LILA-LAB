"""
LILA Lab — Shared LLM Annotation Module

Multi-provider LLM clients and response parsing utilities.

Explicit re-exports:
    from pipelines.shared.llm import call_anthropic, call_openai, call_gemini, call_ollama
    from pipelines.shared.llm import parse_llm_response
"""

from pipelines.shared.llm.clients import call_anthropic, call_gemini, call_ollama, call_openai
from pipelines.shared.llm.parsing import parse_llm_response

__all__ = [
    "call_anthropic",
    "call_openai",
    "call_gemini",
    "call_ollama",
    "parse_llm_response",
]
