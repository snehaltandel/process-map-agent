# Unified CI Coach

This project implements a fully functional conversational Continuous Improvement (CI) coach that orchestrates specialised
coaching experiences for Problem Statements, Value Proposition, SIPOC, Process Maps, Fishbone, 5-Whys, A3, Kaizen, and inline
charting/diagram generation. The implementation follows the specification captured in
[docs/unified-ci-coach-spec.md](docs/unified-ci-coach-spec.md).

## Features

* LangGraph orchestration with a Supervisor router that selects the appropriate coach for each user turn.
* Specialised prompts for each CI artifact that update a shared state model and produce actionable guidance.
* Automatic rendering of process maps and fishbone diagrams to PNG artifacts.
* Inline charting capability (Pareto, histogram, boxplot, run/control, scatter, comparative bar) from pasted CSV datasets.
* Command line interface that stores conversation history and supports exporting the final state to JSON.

## Getting Started

1. **Install dependencies**

   ```bash
   pip install -e .
   ```

2. **Set your OpenAI API key**

   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

   Optionally, change the model by setting `CI_COACH_MODEL` (defaults to `gpt-4o-mini`).

3. **Run the coach**

   ```bash
   ci-coach
   ```

   Paste datasets inside triple-backtick code fences (```` ```csv ... ``` ````) to make them available for charting. Use
   `:state` to inspect the full JSON state, `:reset` to start over, and `:quit` to exit.

Generated diagrams and charts are saved under the `artifacts/` directory. Use the transcript flag to persist the session:

```bash
ci-coach --transcript session.json
```

## Project Structure

```
src/ci_coach/
  app.py            # LangGraph orchestration and dataset ingestion
  charts.py         # Chart rendering utilities
  cli.py            # Command line entry point
  coaches.py        # LangGraph node implementations
  conversation.py   # Conversation/state summarisation helpers
  datasets.py       # Dataset extraction from chat messages
  diagrams.py       # Process map and fishbone rendering
  json_utils.py     # JSON parsing helpers
  llm.py            # LLM factory (OpenAI)
  state.py          # Shared CI state definition
```

The `artifacts/` folder is created on demand and stores generated PNG assets. The `docs/` directory retains the original
product/architecture specification for reference.
