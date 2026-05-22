"""Deterministic agent driven by a fixed list of tool actions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kensho.agents.base import AgentResult, BaseAgent
from kensho.task_spec import TaskSpec
from kensho.tools import WorkspaceTools
from kensho.trace import TraceLogger


class ScriptedAgent(BaseAgent):
    """Executes a scripted sequence of tool calls and stops after submit()."""

    def __init__(self, actions: list[dict[str, Any]]) -> None:
        self._actions = list(actions)

    def run(
        self,
        task: TaskSpec,
        workspace_path: Path,
        trace_logger: TraceLogger,
    ) -> AgentResult:
        tools = WorkspaceTools(workspace_path, trace_logger, task.timeout_seconds)
        steps: list[dict[str, Any]] = []

        for index, action in enumerate(self._actions):
            if tools.submitted:
                break

            tool = action.get("tool")
            if not isinstance(tool, str):
                steps.append(
                    {
                        "index": index,
                        "tool": tool,
                        "result": {"success": False, "error": "action missing tool name"},
                    }
                )
                break

            args = action.get("args", {})
            if not isinstance(args, dict):
                args = {}

            result = tools.dispatch(tool, args)
            steps.append(
                {
                    "index": index,
                    "tool": tool,
                    "arguments": args,
                    "result": result.to_dict(),
                }
            )

            if tool == "submit" and result.success:
                break

        return AgentResult(
            submitted=tools.submitted,
            steps=steps,
            message=tools.submit_message,
        )
