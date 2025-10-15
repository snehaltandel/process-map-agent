"""State definitions for the Unified CI Coach."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """Represents a chat message in the conversation history."""

    role: str
    content: str


@dataclass
class CIState:
    """Container for conversation state shared across the LangGraph."""

    intent: str = ""
    mode: str = "guided"
    user_role: str = "operator"
    problem_statement: Optional[str] = None
    value_proposition: Dict[str, Any] = field(default_factory=dict)
    problem_metrics: List[Dict[str, Any]] = field(default_factory=list)
    problem_scope: Dict[str, Any] = field(default_factory=dict)
    sipoc: Dict[str, Any] = field(default_factory=dict)
    process_map: Dict[str, Any] = field(default_factory=dict)
    vsm: Dict[str, Any] = field(default_factory=dict)
    fishbone: Dict[str, Any] = field(default_factory=dict)
    five_whys: List[Dict[str, Any]] = field(default_factory=list)
    a3: Dict[str, Any] = field(default_factory=dict)
    kaizen_plan: List[Dict[str, Any]] = field(default_factory=list)
    datasets: Dict[str, Any] = field(default_factory=dict)
    charts: List[str] = field(default_factory=list)
    diagrams: List[str] = field(default_factory=list)
    ci_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    latest_user_message: Optional[str] = None
    pending_response: Optional[str] = None
    router_decision: Optional[str] = None
    suggested_next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation of the state."""

        return {
            "intent": self.intent,
            "mode": self.mode,
            "user_role": self.user_role,
            "problem_statement": self.problem_statement,
            "value_proposition": self.value_proposition,
            "problem_metrics": self.problem_metrics,
            "problem_scope": self.problem_scope,
            "sipoc": self.sipoc,
            "process_map": self.process_map,
            "vsm": self.vsm,
            "fishbone": self.fishbone,
            "five_whys": self.five_whys,
            "a3": self.a3,
            "kaizen_plan": self.kaizen_plan,
            "datasets": self.datasets,
            "charts": self.charts,
            "diagrams": self.diagrams,
            "ci_opportunities": self.ci_opportunities,
            "messages": [m.__dict__ for m in self.messages],
            "audit_log": self.audit_log,
            "latest_user_message": self.latest_user_message,
            "pending_response": self.pending_response,
            "router_decision": self.router_decision,
            "suggested_next_steps": self.suggested_next_steps,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CIState":
        """Instantiate a ``CIState`` from a plain dictionary."""

        messages = [Message(**m) for m in data.get("messages", [])]
        return cls(
            intent=data.get("intent", ""),
            mode=data.get("mode", "guided"),
            user_role=data.get("user_role", "operator"),
            problem_statement=data.get("problem_statement"),
            value_proposition=data.get("value_proposition", {}),
            problem_metrics=data.get("problem_metrics", []),
            problem_scope=data.get("problem_scope", {}),
            sipoc=data.get("sipoc", {}),
            process_map=data.get("process_map", {}),
            vsm=data.get("vsm", {}),
            fishbone=data.get("fishbone", {}),
            five_whys=data.get("five_whys", []),
            a3=data.get("a3", {}),
            kaizen_plan=data.get("kaizen_plan", []),
            datasets=data.get("datasets", {}),
            charts=data.get("charts", []),
            diagrams=data.get("diagrams", []),
            ci_opportunities=data.get("ci_opportunities", []),
            messages=messages,
            audit_log=data.get("audit_log", []),
            latest_user_message=data.get("latest_user_message"),
            pending_response=data.get("pending_response"),
            router_decision=data.get("router_decision"),
            suggested_next_steps=data.get("suggested_next_steps", []),
        )


def append_message(state: CIState, role: str, content: str) -> None:
    """Append a chat message to the state's history."""

    state.messages.append(Message(role=role, content=content))
    state.audit_log.append({"role": role, "content": content})
