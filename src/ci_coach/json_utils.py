"""Helpers for working with JSON responses from the LLM."""

from __future__ import annotations

import json
from typing import Any, Dict


def extract_json(response: str) -> Dict[str, Any]:
    """Extract a JSON object from an LLM response.

    The Supervisor and coach prompts instruct the model to respond with raw JSON, but
    this helper defensively parses the first JSON object found in the string and raises
    an informative ``ValueError`` if parsing fails.
    """

    response = response.strip()
    if not response:
        raise ValueError("Empty response from LLM; expected JSON content.")

    # Attempt direct parse first.
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    start = response.find("{")
    end = response.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Unable to locate JSON object in response: {response!r}")

    snippet = response[start : end + 1]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to decode JSON from response snippet. Original response: {response}"
        ) from exc
