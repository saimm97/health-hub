"""
LLM provider adapters.

A tiny strategy interface keeps the rest of the codebase provider-agnostic: the
coach service only ever calls ``get_provider().complete(messages)``. Swapping
Anthropic for OpenAI (or a local model) is a one-line settings change.
"""
from __future__ import annotations

from typing import Protocol

from django.conf import settings


class LLMProvider(Protocol):
    def complete(self, messages: list[dict]) -> str: ...


class StubProvider:
    """Deterministic, offline provider used in dev and tests (no API key)."""

    def complete(self, messages: list[dict]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        return (
            "Here's a suggestion based on your recent activity: keep your sessions "
            "consistent and progress gradually. "
            f'(You asked: "{last_user[:80]}")'
        )


class AnthropicProvider:
    """Adapter for the Anthropic Messages API."""

    def __init__(self) -> None:
        import anthropic  # imported lazily so the dep is optional

        self._client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
        self._model = settings.LLM_MODEL
        self._max_tokens = settings.LLM_MAX_TOKENS

    def complete(self, messages: list[dict]) -> str:
        # Anthropic takes the system prompt separately from the turn list.
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        turns = [m for m in messages if m["role"] in ("user", "assistant")]
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=turns,
        )
        return "".join(block.text for block in resp.content if block.type == "text")


class OpenAIProvider:
    """Adapter for the OpenAI Chat Completions API."""

    def __init__(self) -> None:
        import openai

        self._client = openai.OpenAI(api_key=settings.LLM_API_KEY)
        self._model = settings.LLM_MODEL
        self._max_tokens = settings.LLM_MAX_TOKENS

    def complete(self, messages: list[dict]) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=messages,
        )
        return resp.choices[0].message.content or ""


_PROVIDERS = {
    "stub": StubProvider,
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
}


def get_provider() -> LLMProvider:
    """Instantiate the provider named by ``settings.LLM_PROVIDER``."""
    try:
        return _PROVIDERS[settings.LLM_PROVIDER]()
    except KeyError as exc:
        raise ValueError(
            f"Unknown LLM_PROVIDER {settings.LLM_PROVIDER!r}. "
            f"Choose one of: {', '.join(_PROVIDERS)}."
        ) from exc
