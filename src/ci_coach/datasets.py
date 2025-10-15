"""Utilities for extracting datasets shared during the conversation."""

from __future__ import annotations

import io
import re
from typing import Dict, List, Tuple

import pandas as pd


CODE_BLOCK_PATTERN = re.compile(
    r"```(?P<lang>[a-zA-Z0-9_+-]*)\n(?P<body>.*?)```",
    re.DOTALL,
)


def extract_datasets(message: str) -> List[Tuple[str, pd.DataFrame]]:
    """Extract tabular datasets from fenced code blocks in a message."""

    datasets: List[Tuple[str, pd.DataFrame]] = []
    for index, match in enumerate(CODE_BLOCK_PATTERN.finditer(message), start=1):
        lang = (match.group("lang") or "csv").lower()
        body = match.group("body").strip()
        if lang not in {"csv", "tsv", "text", "table"}:
            continue

        delimiter = "," if lang != "tsv" else "\t"
        try:
            df = pd.read_csv(io.StringIO(body), delimiter=delimiter)
        except Exception:
            continue

        datasets.append((f"dataset_{index}", df))
    return datasets


def dataframe_preview(df: pd.DataFrame, max_rows: int = 5) -> str:
    """Return a small textual preview of a DataFrame."""

    preview = df.head(max_rows).to_markdown(index=False)
    return preview
