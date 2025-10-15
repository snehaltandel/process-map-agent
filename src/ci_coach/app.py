"""Application orchestration for the Unified CI Coach."""

from __future__ import annotations

from typing import Dict

from langgraph.graph import END, StateGraph

from .coaches import (
    a3_node,
    charts_node,
    five_whys_node,
    fishbone_node,
    kaizen_node,
    problem_node,
    process_map_node,
    sipoc_node,
    supervisor_node,
    value_prop_node,
)
from .datasets import dataframe_preview, extract_datasets
from .state import CIState, append_message


def _route_from_supervisor(state: Dict[str, any]) -> str:
    decision = state.get("router_decision") or "problem"
    if decision not in {
        "problem",
        "value_prop",
        "process_map",
        "sipoc",
        "fishbone",
        "five_whys",
        "a3",
        "kaizen",
        "charts",
        "idle",
    }:
        return "problem"
    return decision


class CICoachApp:
    """High level interface for running the CI Coach conversation."""

    def __init__(self) -> None:
        self.state = CIState()
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(dict)
        graph.add_node("supervisor", supervisor_node)
        graph.add_node("problem", problem_node)
        graph.add_node("value_prop", value_prop_node)
        graph.add_node("process_map", process_map_node)
        graph.add_node("sipoc", sipoc_node)
        graph.add_node("fishbone", fishbone_node)
        graph.add_node("five_whys", five_whys_node)
        graph.add_node("a3", a3_node)
        graph.add_node("kaizen", kaizen_node)
        graph.add_node("charts", charts_node)

        graph.set_entry_point("supervisor")
        graph.add_conditional_edges(
            "supervisor",
            _route_from_supervisor,
            {
                "problem": "problem",
                "value_prop": "value_prop",
                "process_map": "process_map",
                "sipoc": "sipoc",
                "fishbone": "fishbone",
                "five_whys": "five_whys",
                "a3": "a3",
                "kaizen": "kaizen",
                "charts": "charts",
                "idle": END,
            },
        )

        for node in [
            "problem",
            "value_prop",
            "process_map",
            "sipoc",
            "fishbone",
            "five_whys",
            "a3",
            "kaizen",
            "charts",
        ]:
            graph.add_edge(node, "supervisor")

        return graph.compile()

    def reset(self) -> None:
        self.state = CIState()

    def send(self, message: str) -> str:
        """Process a user message and return the assistant response."""

        append_message(self.state, "user", message)
        self.state.latest_user_message = message

        datasets = extract_datasets(message)
        for name, df in datasets:
            identifier = name
            counter = 1
            while identifier in self.state.datasets:
                counter += 1
                identifier = f"{name}_{counter}"
            self.state.datasets[identifier] = df
            preview = dataframe_preview(df)
            self.state.audit_log.append(
                {
                    "node": "dataset_ingest",
                    "dataset": identifier,
                    "preview": preview,
                }
            )

        result_state = self._graph.invoke(self.state.to_dict())
        self.state = CIState.from_dict(result_state)

        response = self.state.pending_response or "Let me know how else I can help."
        return response

    def export_state(self) -> Dict[str, any]:
        """Return a dictionary representation of the full state."""

        return self.state.to_dict()
