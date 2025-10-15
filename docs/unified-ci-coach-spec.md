# Unified CI Coach — Design & Specification

**Goal:** A one-stop conversational **Continuous Improvement (CI) Coach** that orchestrates Problem Statement, A3, SIPOC, Process Map, Fishbone, 5-Whys, Value Proposition, and Kaizen workflows. It can **render diagrams**, **generate charts from data in-chat**, and export deliverables.

**Tech:** LangGraph (orchestration), OpenAI (reasoning + extraction), Python runtime (charting/analysis), Diagram tools (Mermaid/Graphviz), Vector KB (CI knowledge), File services (export).

---

## 1. Outcomes & KPIs

- **Time to first artifact** (A3, map, or SIPOC) ≤ 10 minutes.
- **Guided → Quick completion rate** ≥ 80% for first-time users.
- **CI opportunity yield** ≥ 5 per engagement on average.
- **Re-use of artifacts across coaches** ≥ 90% without re-entry.

## 2. Users & Modes

### Personas

- **Beginner Operators / Staff:** step-by-step guidance, examples, micro-tutorials.
- **Process Engineers / BB/GB:** quick data pasting, CSV/JSON upload, fast exports.
- **Leaders:** dashboard summaries, status of CI journey, KPIs, before/after visuals.

### Interaction Modes

- **Guided Mode** — Q&A, templates, guardrails.
- **Quick Mode** — paste table/CSV/JSON → instant artifact.
- **Review Mode** — validate/critique existing artifacts, suggest improvements.

## 3. End-to-End Journey Map

1. **Define** → Problem Statement Coach (+ Value Proposition).
2. **Map** → Process Map Coach (or VSM if scope is high-level).
3. **Analyze** → SIPOC, Fishbone, 5-Whys, baseline metrics & charts.
4. **Improve** → Kaizen Coach (countermeasures, pilots, PDSA).
5. **Control** → A3 finalize, control charts, SOP alignment, handoff to Ops.

The **Supervisor** preserves context and routes between sub-coaches.

## 4. High-Level Architecture

```mermaid
flowchart LR
  subgraph UI
    Chat[Conversational UI]
    Upload[CSV/JSON/XLSX Upload]
    VizPane[Chart/Diagram Pane]
  end

  subgraph Orchestration
    Sup[Supervisor / Intent Router]
    Elicit[Problem Statement Coach]
    VPC[Value Prop Coach]
    Map[Process Map Coach]
    VSM[Value Stream Mapper]
    SIPOC[SIPOC Coach]
    Fish[Fishbone Coach]
    W5[5-Whys Coach]
    A3[A3 Coach]
    Kaizen[Kaizen Coach]
  end

  subgraph Tools
    Py[Python Sandbox (charts, stats)]
    Diag[Diagram Renderer (Mermaid/Graphviz)]
    Metrics[Metrics Calculator]
    Export[Export Service]
    KB[Vector Knowledge Base]
  end

  Chat --> Sup
  Upload --> Sup
  Sup --> Elicit --> Map --> Fish --> W5 --> A3 --> Kaizen
  Sup --> VPC
  Sup --> VSM
  Sup --> SIPOC

  Sup --> Py
  Sup --> Diag
  Sup --> Metrics
  Sup <--> KB
  Diag --> VizPane
  Py --> VizPane
  Export --> Chat
```

## 5. Orchestration with LangGraph

### Shared State

```python
from typing import TypedDict, List, Dict, Any, Optional

class CIState(TypedDict):
    intent: str
    mode: str                 # guided|quick|review
    user_role: str            # operator|engineer|lead|coach
    problem_statement: str
    value_proposition: Dict[str, Any]
    sipoc: Dict[str, Any]
    process_map: Dict[str, Any]     # JSON schema from Process Map Coach
    vsm: Dict[str, Any]
    fishbone: Dict[str, Any]
    five_whys: List[Dict[str, Any]]
    a3: Dict[str, Any]
    kaizen_plan: List[Dict[str, Any]]
    datasets: Dict[str, Any]        # uploaded tables
    charts: List[str]               # paths/URIs
    diagrams: List[str]             # paths/URIs
    ci_opportunities: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]  # chat history
    audit_log: List[Dict[str, Any]]
```

### Nodes

- **Supervisor / Intent Router** — detect user intent, pick coach, manage transitions, enforce governance.
- **Problem Statement Coach** — SMART problem, CTQ, baseline scope & success criteria.
- **Value Proposition Coach** — stakeholder value, impact framing, must-haves vs nice-to-haves.
- **Process Map Coach** — swimlane/flowchart; switches to **VSM** for high-level scope.
- **SIPOC Coach** — Suppliers, Inputs, Process (5-7 steps), Outputs, Customers.
- **Fishbone Coach** — categories (Methods, Machines, Materials, Manpower, Measurement, Environment); evidence links.
- **5-Whys Coach** — linear chains tied to Fishbone nodes; terminate on controllable root cause.
- **A3 Coach** — composes Problem → Current State → Analysis → Countermeasures → Plan → Follow-up.
- **Kaizen Coach** — countermeasures, pilot design, owner/RACI, PDCA cadence.
- **Python Sandbox Tool Node** — chart rendering, stats, simulations.
- **Diagram Renderer Tool Node** — Mermaid/Graphviz → SVG/PNG; embeds in chat.

### Routing Edges (Simplified)

```python
edges = {
  "start": ["Supervisor"],
  "Supervisor": ["Problem", "Map", "VSM", "SIPOC", "Fishbone", "Whys", "A3", "Kaizen", "PythonCharts", "Diagram"],
  "Problem": ["Map", "SIPOC"],
  "Map": ["Fishbone", "Whys", "A3"],
  "VSM": ["Map", "A3"],
  "Fishbone": ["Whys", "A3"],
  "Whys": ["A3"],
  "A3": ["Kaizen"],
  "Kaizen": ["end"]
}
```

## 6. Prompt Packs

Externalized prompt packs provide consistent coaching tone and guardrails:

- `problem.yaml` — SMART, scope, constraints, CTQ extraction.
- `map.yaml` — lane suggestions, handoff detection, compliance tone (GxP-friendly).
- `vsm.yaml` — takt, CT, WT, WIP, bottleneck, future-state heuristics.
- `sipoc.yaml` — crisp 5–7 process steps, customer needs matrix.
- `fishbone.yaml` — evidence-backed causes; ask for data.
- `whys.yaml` — 3–5 why chains; stop when cause is specific + controllable.
- `a3.yaml` — compose sections + link artifacts; produce exec summary.
- `kaizen.yaml` — countermeasure backlog (impact/effort), owners, due dates, PDCA.
- `charts.yaml` — safe Python spec generation rules.

## 7. Python Charting in Chat

1. User pastes CSV/table or uploads file.
2. LLM validates/cleans → normalized DataFrame.
3. Python sandbox executes recipes to render Matplotlib figures (no external net).
4. Images embedded back into chat; code block optionally shown for reproducibility.

**Prebuilt Recipes:** Pareto of defect categories, Histogram/Boxplot of cycle time, Run/Control Chart (X-bar/R or I-MR), Lead-time vs WIP scatter (Little’s Law intuition), Before/After comparison bars.

**Safety & Controls:** resource/time limits; sanitization; deterministic seeds; no PII.

## 8. Diagram Rendering

- **Process Map Coach** outputs Mermaid (swimlane/flow).
- **VSM** includes icons for process boxes, data boxes, inventory triangles, push/pull, info flow.
- **Fishbone** auto-layout categories with cause nodes.
- **Exports** supply SVG/PNG plus source Mermaid/Graphviz.

## 9. Data Models (Excerpts)

### Process Map JSON

(see Process Map Coach spec). Keys: `roles[]`, `steps[]`, `edges[]`, `systems[]`, `metrics`.

### VSM JSON

```json
{
  "name": "E2E Material to Release",
  "demand_per_day": 50,
  "stages": [
    {"id":"s1","name":"Receive","ct_min":12,"wt_min":30,"wip":20},
    {"id":"s2","name":"Sample","ct_min":20,"wt_min":240,"wip":35}
  ],
  "lead_time_min": 0,
  "value_add_time_min": 0,
  "bottleneck_stage_id": ""
}
```

### A3 JSON

```json
{
  "title":"Reduce Raw Material Release Time",
  "problem":"Production delays due to QC release lag",
  "current_state": {"lead_time_days": 3.2, "%VA": 0.18},
  "analysis": {"fishbone_ids": ["f1"], "why_chains": []},
  "countermeasures": [{"id":"c1","idea":"LIMS queue triage","impact":"High","effort":"Medium"}],
  "plan": [{"task":"Implement triage","owner":"QC Lead","due":"2025-11-15"}],
  "follow_up": [{"metric":"Lead time","target":"-25%"}]
}
```

## 10. UX Flows

- **Start:** "Tell me your goal. I can help with Problem, Map/VSM, SIPOC, Fishbone/5-Whys, A3, Kaizen, or charts from your data."
- **Intent Confirmation:** show 3 suggested next actions plus Quick/Guided toggle.
- **Inline Visuals:** charts & diagrams render in a right-hand pane; downloadable.
- **Smart Handoffs:** outputs automatically seed the next coach (no re-typing).
- **Leader View:** progress tracker (Problem → Improve → Control), KPI cards, artifact links.

## 11. Compliance, Security, Audit

- **GxP tone guardrails** (non-prescriptive wording, factual descriptions).
- **PHI/PII scrubbing** on uploads.
- **Audit log** of prompts, tool calls, artifact versions, exports.
- **RBAC** for viewing/exporting artifacts; watermark with environment + timestamp.

## 12. Non-Functional Requirements

- **Latency:** <5s for first preview (Quick Mode); <2s incremental renders.
- **Resilience:** JSON source of truth; recover diagrams from JSON any time.
- **Observability:** traces per node; coach usage metrics; CI outcome tracking.

## 13. Minimal Viable Release (6 Weeks)

- **Week 1–2:** Supervisor + Problem Coach + Python charts (Pareto, Histogram).
- **Week 3–4:** Process Map Coach + Mermaid renderer + VSM current-state.
- **Week 5:** Fishbone + 5-Whys + A3 composer.
- **Week 6:** Kaizen planner + exports (PDF/PNG/SVG/JSON) + leader dashboard.

## 14. Example Interaction

> **User:** "Here’s a CSV of cycle times by batch; show a Pareto of defect reasons too."
>
> **Coach:** cleans data → renders histogram + Pareto → highlights long tail.
>
> **Coach:** "Want to map the process step causing the top 20% of delays?" → launches Process Map Coach pre-filled.

## 15. Open Questions

- Preferred export destinations (Confluence/SharePoint/Smartsheet/Email)?
- Site-standard lane names & glossary for Process Map defaults?
- Control chart standards (I-MR vs X-bar/R) by area?
- Data retention & anonymization policies for uploaded datasets?
