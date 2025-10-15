"""Utility helpers for constructing language model instances."""

from __future__ import annotations

import os
from functools import lru_cache

from langchain_openai import ChatOpenAI


@lru_cache(maxsize=1)
def get_llm(model: str | None = None, temperature: float = 0.1) -> ChatOpenAI:
    """Return a shared ``ChatOpenAI`` instance configured from environment variables."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is required to run the CI Coach."
        )

    return ChatOpenAI(
        api_key=api_key,
        model=model or os.getenv("CI_COACH_MODEL", "gpt-4o-mini"),
        temperature=temperature,
    )
