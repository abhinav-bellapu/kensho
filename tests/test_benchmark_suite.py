from __future__ import annotations

from pathlib import Path

import pytest

from kensho.runner import run_task
from kensho.task_spec import load_task_spec

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmarks/starter_python/tasks"


def _task_yaml_files() -> list[Path]:
    return sorted(TASKS_DIR.glob("*.yaml"))


@pytest.mark.parametrize("task_yaml", _task_yaml_files(), ids=lambda p: p.stem)
def test_task_yaml_loads(task_yaml: Path) -> None:
    spec = load_task_spec(task_yaml)
    assert spec.id == task_yaml.stem
    assert spec.repo_path.is_dir()


def test_task_ids_are_unique() -> None:
    ids = [load_task_spec(path).id for path in _task_yaml_files()]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("task_yaml", _task_yaml_files(), ids=lambda p: p.stem)
@pytest.mark.integration
def test_task_fails_without_agent(task_yaml: Path) -> None:
    result = run_task(task_yaml)
    assert result.status == "failed", (
        f"expected {task_yaml.stem} to fail without an agent, got {result.status}"
    )
    assert result.score == 0.0
