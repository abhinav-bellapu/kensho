"""Task specification loaded from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = (
    "id",
    "name",
    "repo_path",
    "prompt",
    "setup_commands",
    "test_commands",
    "timeout_seconds",
)


@dataclass(frozen=True)
class TaskSpec:
    id: str
    name: str
    repo_path: Path
    prompt: str
    setup_commands: list[str]
    test_commands: list[str]
    timeout_seconds: int


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"task field '{key}' must be a non-empty string")
    return value


def _require_str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"task field '{key}' must be a non-empty list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"task field '{key}' must contain only non-empty strings")
    return value


def _require_positive_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"task field '{key}' must be a positive integer")
    return value


def load_task_spec(task_yaml: Path) -> TaskSpec:
    """Load and validate a task specification from a YAML file."""
    task_yaml = task_yaml.resolve()
    raw = yaml.safe_load(task_yaml.read_text())
    if not isinstance(raw, dict):
        raise ValueError("task YAML must be a mapping")

    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise ValueError(f"task YAML missing required fields: {', '.join(missing)}")

    repo_path = Path(_require_str(raw, "repo_path"))
    if not repo_path.is_absolute():
        repo_path = (task_yaml.parent / repo_path).resolve()

    return TaskSpec(
        id=_require_str(raw, "id"),
        name=_require_str(raw, "name"),
        repo_path=repo_path,
        prompt=_require_str(raw, "prompt"),
        setup_commands=_require_str_list(raw, "setup_commands"),
        test_commands=_require_str_list(raw, "test_commands"),
        timeout_seconds=_require_positive_int(raw, "timeout_seconds"),
    )
