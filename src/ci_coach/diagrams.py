"""Diagram rendering for process maps and fishbone analysis."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ARTIFACTS_DIR = Path(os.getenv("CI_COACH_ARTIFACTS", "artifacts"))
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def render_process_map(process_map: Dict) -> Path:
    """Render a simple left-to-right process map diagram."""

    steps: List[Dict] = process_map.get("steps", [])
    roles = {role["id"]: role["name"] for role in process_map.get("roles", [])}

    if not steps:
        raise ValueError("No steps found in process map definition.")

    fig, ax = plt.subplots(figsize=(max(10, len(steps) * 2.5), 4))
    ax.axis("off")

    lane_positions = {role_id: idx for idx, role_id in enumerate(roles)}
    num_lanes = max(len(lane_positions), 1)

    for idx, step in enumerate(steps):
        role_id = step.get("role_id")
        lane_idx = lane_positions.get(role_id, 0)
        x = idx * 2.5 + 1
        y = (num_lanes - lane_idx) * 1.5
        box = FancyBboxPatch(
            (x, y),
            2.2,
            0.9,
            boxstyle="round,pad=0.2",
            linewidth=1.2,
            edgecolor="#1f77b4",
            facecolor="#e8f1fb",
        )
        ax.add_patch(box)
        ax.text(
            x + 1.1,
            y + 0.45,
            step.get("name", "Step"),
            ha="center",
            va="center",
            fontsize=10,
            wrap=True,
        )
        ax.text(
            x + 1.1,
            y + 1.0,
            roles.get(role_id, ""),
            ha="center",
            va="bottom",
            fontsize=8,
            color="#555555",
        )

    for edge in process_map.get("edges", []):
        try:
            start_idx = next(i for i, s in enumerate(steps) if s["id"] == edge["from"])
            end_idx = next(i for i, s in enumerate(steps) if s["id"] == edge["to"])
        except StopIteration:
            continue
        start_x = start_idx * 2.5 + 3.2
        end_x = end_idx * 2.5 + 1
        start_y = (num_lanes - lane_positions.get(steps[start_idx].get("role_id"), 0)) * 1.5 + 0.45
        end_y = (num_lanes - lane_positions.get(steps[end_idx].get("role_id"), 0)) * 1.5 + 0.45
        ax.annotate(
            "",
            xy=(end_x, end_y),
            xytext=(start_x, start_y),
            arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.2),
        )
        if note := edge.get("note"):
            ax.text(
                (start_x + end_x) / 2,
                (start_y + end_y) / 2 + 0.2,
                note,
                ha="center",
                va="bottom",
                fontsize=8,
                color="#555555",
            )

    ax.set_ylim(0, (num_lanes + 2) * 1.5)
    artifact_path = ARTIFACTS_DIR / "process_map.png"
    fig.tight_layout()
    fig.savefig(artifact_path, dpi=150)
    plt.close(fig)
    return artifact_path


def render_fishbone(fishbone: Dict) -> Path:
    """Render a fishbone diagram based on categories and causes."""

    categories = fishbone.get("categories", [])
    if not categories:
        raise ValueError("Fishbone definition missing categories.")

    fig, ax = plt.subplots(figsize=(10, max(5, len(categories) * 1.5)))
    ax.axis("off")

    spine_x = [0.5, 9.5]
    spine_y = [len(categories) / 2, len(categories) / 2]
    ax.plot(spine_x, spine_y, color="#1f77b4", linewidth=2)

    for idx, category in enumerate(categories):
        direction = -1 if idx % 2 == 0 else 1
        base_y = spine_y[0] + direction * (idx + 1) * 0.6
        ax.plot(
            [2.0, 8.5],
            [spine_y[0], base_y],
            color="#1f77b4",
            linewidth=1.5,
        )
        ax.text(8.8, base_y, category.get("name", "Category"), fontsize=11, va="center")
        for c_idx, cause in enumerate(category.get("causes", [])):
            cy = base_y + direction * (c_idx + 1) * 0.4
            ax.plot([4.0, 7.0], [base_y, cy], color="#4c78a8", linewidth=1)
            label = cause.get("statement", "Cause")
            if evidence := cause.get("evidence"):
                label += f"\nEvidence: {evidence}"
            ax.text(7.1, cy, label, fontsize=9, va="center")

    ax.text(0.4, spine_y[0], fishbone.get("effect", "Problem"), fontsize=12, va="center")
    artifact_path = ARTIFACTS_DIR / "fishbone.png"
    fig.tight_layout()
    fig.savefig(artifact_path, dpi=150)
    plt.close(fig)
    return artifact_path
