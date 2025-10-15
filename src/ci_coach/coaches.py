"""LangGraph nodes implementing each specialised CI coach."""

from __future__ import annotations

from typing import Any, Dict

from langchain.schema import SystemMessage

from .charts import ChartRenderer, ChartSpec
from .conversation import build_state_summary, to_langchain_messages
from .diagrams import render_fishbone, render_process_map
from .json_utils import extract_json
from .llm import get_llm
from .prompts import (
    A3_PROMPT,
    CHART_PROMPT,
    FISHBONE_PROMPT,
    FIVE_WHYS_PROMPT,
    KAIZEN_PROMPT,
    PROCESS_MAP_PROMPT,
    PROBLEM_PROMPT,
    SIPOC_PROMPT,
    SUPERVISOR_PROMPT,
    VALUE_PROP_PROMPT,
)
from .state import CIState, append_message


def _prepare_conversation(ci_state: CIState) -> Dict[str, Any]:
    conversation = to_langchain_messages(ci_state)
    summary = build_state_summary(ci_state)
    conversation_with_summary = [SystemMessage(content=f"Context summary:\n{summary}")]
    conversation_with_summary.extend(conversation)
    return {
        "conversation": conversation_with_summary,
        "latest_message": ci_state.latest_user_message or "",
    }


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    if not ci_state.latest_user_message:
        return ci_state.to_dict()

    llm = get_llm(temperature=0.0)
    prompt_inputs = _prepare_conversation(ci_state)
    messages = SUPERVISOR_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.intent = data.get("updated_intent", ci_state.intent)
    ci_state.mode = data.get("mode", ci_state.mode)
    ci_state.router_decision = data.get("next_node", "problem")
    ci_state.suggested_next_steps = data.get("suggested_next", [])
    ci_state.audit_log.append(
        {
            "node": "supervisor",
            "decision": ci_state.router_decision,
            "intent": ci_state.intent,
            "assistant_message": data.get("assistant_message"),
        }
    )
    return ci_state.to_dict()


def problem_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = PROBLEM_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.problem_statement = data.get("problem_statement", ci_state.problem_statement)
    ci_state.problem_metrics = data.get("metrics", ci_state.problem_metrics)
    ci_state.problem_scope = data.get("scope", ci_state.problem_scope)
    ci_state.ci_opportunities = data.get("ci_opportunities", ci_state.ci_opportunities)
    message = data.get("message", "Here is the refreshed problem statement.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def value_prop_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = VALUE_PROP_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.value_proposition = {
        "stakeholders": data.get("stakeholders", []),
        "impact": data.get("impact", {}),
        "requirements": data.get("requirements", {}),
    }
    message = data.get("message", "Value proposition updated.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def sipoc_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = SIPOC_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.sipoc = {
        "suppliers": data.get("suppliers", []),
        "inputs": data.get("inputs", []),
        "process_steps": data.get("process_steps", []),
        "outputs": data.get("outputs", []),
        "customers": data.get("customers", []),
    }
    message = data.get("message", "SIPOC drafted.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def process_map_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = PROCESS_MAP_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.process_map = {
        "roles": data.get("roles", []),
        "steps": data.get("steps", []),
        "edges": data.get("edges", []),
        "systems": data.get("systems", []),
    }
    message = data.get("message", "Process map drafted.")
    try:
        diagram_path = render_process_map(ci_state.process_map)
        ci_state.diagrams.append(str(diagram_path))
        message += f"\nProcess map diagram exported to {diagram_path}."
    except Exception as exc:  # pragma: no cover - rendering errors logged in audit
        ci_state.audit_log.append({"node": "process_map", "error": str(exc)})
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def fishbone_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = FISHBONE_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.fishbone = {
        "categories": data.get("categories", []),
        "effect": data.get("effect", ci_state.problem_statement or "Problem"),
    }
    message = data.get("message", "Fishbone diagram drafted.")
    try:
        diagram_path = render_fishbone(ci_state.fishbone)
        ci_state.diagrams.append(str(diagram_path))
        message += f"\nFishbone diagram exported to {diagram_path}."
    except Exception as exc:
        ci_state.audit_log.append({"node": "fishbone", "error": str(exc)})
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def five_whys_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = FIVE_WHYS_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.five_whys = data.get("chains", ci_state.five_whys)
    message = data.get("message", "5-Whys analysis drafted.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def a3_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = A3_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.a3 = {
        "summary": data.get("summary"),
        "background": data.get("background"),
        "current_state": data.get("current_state"),
        "analysis": data.get("analysis"),
        "countermeasures": data.get("countermeasures"),
        "plan": data.get("plan"),
        "follow_up": data.get("follow_up"),
    }
    message = data.get("message", "A3 composed.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def kaizen_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = KAIZEN_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    ci_state.kaizen_plan = data.get("backlog", ci_state.kaizen_plan)
    ci_state.audit_log.append({"node": "kaizen", "pilot_plan": data.get("pilot_plan")})
    message = data.get("message", "Kaizen backlog drafted.")
    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()


def charts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ci_state = CIState.from_dict(state)
    if not ci_state.datasets:
        message = "I didn't detect a dataset. Please paste a CSV in a code block."
        append_message(ci_state, "assistant", message)
        ci_state.pending_response = message
        return ci_state.to_dict()

    llm = get_llm()
    prompt_inputs = _prepare_conversation(ci_state)
    messages = CHART_PROMPT.format_messages(**prompt_inputs)
    response = llm.invoke(messages)
    data = extract_json(response.content)

    spec = ChartSpec(
        dataset_name=data.get("dataset_name", next(iter(ci_state.datasets))),
        chart_type=data.get("chart_type", "histogram"),
        value_column=data.get("value_column"),
        category_column=data.get("category_column"),
        secondary_column=data.get("secondary_column"),
        title=data.get("title", "CI Chart"),
    )

    renderer = ChartRenderer(ci_state.datasets)
    try:
        chart_path = renderer.render(spec)
        ci_state.charts.append(str(chart_path))
        message = data.get(
            "message",
            f"Chart created at {chart_path}.",
        )
        message += f"\nChart saved to {chart_path}."
    except Exception as exc:
        message = f"Unable to render chart: {exc}"
        ci_state.audit_log.append({"node": "charts", "error": str(exc)})

    append_message(ci_state, "assistant", message)
    ci_state.pending_response = message
    return ci_state.to_dict()
