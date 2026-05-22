"""Load and validate scripted agent action files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_script(script_path: Path) -> list[dict[str, Any]]:
    """Load a JSON script file into actions compatible with ScriptedAgent."""
    script_path = script_path.resolve()
    raw = json.loads(script_path.read_text())

    if not isinstance(raw, list):
        raise ValueError("script JSON must be a list of actions")

    actions: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"action {index} must be an object")

        tool = item.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError(f"action {index} must include a non-empty tool string")

        args = item.get("args", {})
        if not isinstance(args, dict):
            raise ValueError(f"action {index} args must be an object")

        actions.append({"tool": tool, "args": args})

    return actions
