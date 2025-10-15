"""Helpers for working with LangChain chat messages."""

from __future__ import annotations

from typing import List

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage

from .state import CIState, Message


def to_langchain_messages(state: CIState) -> List[BaseMessage]:
    """Convert stored conversation history to LangChain messages."""

    converted: List[BaseMessage] = []
    for msg in state.messages:
        if msg.role == "system":
            converted.append(SystemMessage(content=msg.content))
        elif msg.role == "assistant":
            converted.append(AIMessage(content=msg.content))
        else:
            converted.append(HumanMessage(content=msg.content))
    return converted


def build_state_summary(state: CIState) -> str:
    """Return a textual summary of the known artifacts for prompting."""

    sections = []
    if state.problem_statement:
        sections.append(f"Problem Statement: {state.problem_statement}")
    if state.value_proposition:
        sections.append(f"Value Proposition: {state.value_proposition}")
    if state.sipoc:
        sections.append(f"SIPOC: {state.sipoc}")
    if state.process_map:
        sections.append(f"Process Map: {state.process_map}")
    if state.fishbone:
        sections.append(f"Fishbone: {state.fishbone}")
    if state.five_whys:
        sections.append(f"5-Whys: {state.five_whys}")
    if state.a3:
        sections.append(f"A3: {state.a3}")
    if state.kaizen_plan:
        sections.append(f"Kaizen Plan: {state.kaizen_plan}")
    if state.datasets:
        dataset_names = ", ".join(state.datasets.keys())
        sections.append(f"Datasets available: {dataset_names}")
    if state.charts:
        sections.append(f"Charts generated: {state.charts}")
    if state.diagrams:
        sections.append(f"Diagrams generated: {state.diagrams}")
    return "\n".join(sections) if sections else "No artifacts captured yet."
