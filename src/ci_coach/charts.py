"""Chart rendering utilities for the CI Coach."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


ARTIFACTS_DIR = Path(os.getenv("CI_COACH_ARTIFACTS", "artifacts"))
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ChartSpec:
    dataset_name: str
    chart_type: str
    value_column: str
    category_column: Optional[str] = None
    secondary_column: Optional[str] = None
    title: str = ""


class ChartRenderer:
    """Render charts from ``ChartSpec`` instructions."""

    def __init__(self, datasets: dict[str, pd.DataFrame]):
        self.datasets = datasets

    def render(self, spec: ChartSpec) -> Path:
        if spec.dataset_name not in self.datasets:
            raise KeyError(f"Dataset {spec.dataset_name!r} not found. Available: {list(self.datasets)}")

        df = self.datasets[spec.dataset_name]
        chart_type = spec.chart_type.lower()

        fig, ax = plt.subplots(figsize=(8, 5))

        if chart_type == "pareto":
            self._pareto(df, spec, ax)
        elif chart_type == "histogram":
            self._histogram(df, spec, ax)
        elif chart_type == "boxplot":
            self._boxplot(df, spec, ax)
        elif chart_type in {"run", "control"}:
            self._run_chart(df, spec, ax)
        elif chart_type == "scatter":
            self._scatter(df, spec, ax)
        elif chart_type == "bar_compare":
            self._bar_compare(df, spec, ax)
        else:
            raise ValueError(f"Unsupported chart type: {spec.chart_type}")

        ax.set_title(spec.title or spec.chart_type.title())
        ax.grid(True, axis="y", alpha=0.2)
        fig.tight_layout()

        artifact_path = ARTIFACTS_DIR / f"chart_{spec.chart_type}_{spec.dataset_name}.png"
        fig.savefig(artifact_path, dpi=150)
        plt.close(fig)
        return artifact_path

    def _pareto(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        if spec.category_column is None:
            raise ValueError("Pareto charts require a category_column.")

        agg = (
            df.groupby(spec.category_column)[spec.value_column]
            .sum()
            .sort_values(ascending=False)
        )
        cumulative = agg.cumsum() / agg.sum()
        ax.bar(agg.index, agg.values, color="#1f77b4")
        ax2 = ax.twinx()
        ax2.plot(agg.index, cumulative.values, color="#ff7f0e", marker="o")
        ax2.axhline(0.8, color="gray", linestyle="--", linewidth=1)
        ax.set_ylabel(spec.value_column)
        ax2.set_ylabel("Cumulative %")
        ax2.set_ylim(0, 1.05)
        ax.tick_params(axis="x", rotation=45, ha="right")

    def _histogram(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        sns.histplot(df[spec.value_column].dropna(), bins=15, ax=ax, color="#1f77b4")
        ax.set_xlabel(spec.value_column)
        ax.set_ylabel("Frequency")

    def _boxplot(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        sns.boxplot(y=df[spec.value_column].dropna(), ax=ax, color="#1f77b4")
        ax.set_ylabel(spec.value_column)

    def _run_chart(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        if spec.secondary_column is None:
            raise ValueError("Run/Control charts require a secondary_column for ordering.")

        ordered = df.sort_values(spec.secondary_column)
        ax.plot(ordered[spec.secondary_column], ordered[spec.value_column], marker="o")
        mean_val = ordered[spec.value_column].mean()
        ax.axhline(mean_val, color="red", linestyle="--", linewidth=1, label="Mean")
        if spec.chart_type == "control":
            std = ordered[spec.value_column].std()
            ax.axhline(mean_val + 3 * std, color="gray", linestyle=":", linewidth=1)
            ax.axhline(mean_val - 3 * std, color="gray", linestyle=":", linewidth=1)
        ax.set_xlabel(spec.secondary_column)
        ax.set_ylabel(spec.value_column)
        ax.legend()

    def _scatter(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        if spec.secondary_column is None:
            raise ValueError("Scatter charts require a secondary_column.")
        ax.scatter(df[spec.secondary_column], df[spec.value_column], alpha=0.7)
        ax.set_xlabel(spec.secondary_column)
        ax.set_ylabel(spec.value_column)

    def _bar_compare(self, df: pd.DataFrame, spec: ChartSpec, ax: plt.Axes) -> None:
        if spec.category_column is None or spec.secondary_column is None:
            raise ValueError("bar_compare charts require category and secondary columns.")
        pivot = df.pivot_table(
            index=spec.category_column,
            columns=spec.secondary_column,
            values=spec.value_column,
            aggfunc="mean",
        )
        pivot.plot(kind="bar", ax=ax)
        ax.set_ylabel(spec.value_column)
        ax.tick_params(axis="x", rotation=45, ha="right")
