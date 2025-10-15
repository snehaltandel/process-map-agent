"""Command line interface for interacting with the Unified CI Coach."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .app import CICoachApp


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Continuous Improvement Coach")
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Optional path to save the final conversation transcript as JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    app = CICoachApp()

    print("Unified CI Coach ready. Paste CSV data inside triple backticks to load datasets.")
    print("Type :reset to start over, :state to export current state, or :quit to exit.\n")

    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {":quit", ":exit"}:
                break
            if user_input.lower() == ":reset":
                app.reset()
                print("Coach: Session reset. How can I help next?")
                continue
            if user_input.lower() == ":state":
                state = app.export_state()
                print(json.dumps(state, indent=2, default=str))
                continue

            response = app.send(user_input)
            print(f"Coach: {response}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")

    if args.transcript:
        args.transcript.write_text(json.dumps(app.export_state(), indent=2, default=str))
        print(f"Transcript saved to {args.transcript}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main(sys.argv[1:])
