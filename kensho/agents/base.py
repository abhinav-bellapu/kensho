"""Agent abstractions for interacting with benchmark workspaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kensho.task_spec import TaskSpec
from kensho.trace import TraceLogger


@dataclass
class AgentResult:
    submitted: bool
    steps: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""


class BaseAgent(ABC):
    """Runs inside a workspace and uses tools to modify the benchmark repo."""

    @abstractmethod
    def run(
        self,
        task: TaskSpec,
        workspace_path: Path,
        trace_logger: TraceLogger,
    ) -> AgentResult:
        """Execute the agent against the task workspace."""
