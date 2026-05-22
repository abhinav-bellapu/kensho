from __future__ import annotations

import json
from pathlib import Path

import pytest

from kensho.runner import run_task

ROOT = Path(__file__).resolve().parents[1]
STARTER_TASK = ROOT / "benchmarks/starter_python/tasks/fix_slugify_unicode.yaml"


def _write_task(tmp_path: Path, repo: Path, setup: list[str], tests: list[str]) -> Path:
    task_yaml = tmp_path / "task.yaml"
    setup_lines = "".join(f"  - {json.dumps(cmd)}\n" for cmd in setup)
    test_lines = "".join(f"  - {json.dumps(cmd)}\n" for cmd in tests)
    task_yaml.write_text(
        f"""
id: mini_task
name: Mini Task
repo_path: {repo}
prompt: Run commands.
setup_commands:
{setup_lines}test_commands:
{test_lines}timeout_seconds: 30
"""
    )
    return task_yaml


def test_run_passes_when_tests_succeed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ok.txt").write_text("ok")
    task_yaml = _write_task(
        tmp_path, repo, setup=["/usr/bin/true"], tests=["/usr/bin/true", "test -f ok.txt"]
    )
    result = run_task(task_yaml)
    assert result.status == "passed"
    assert result.score == 1.0
    assert result.task_id == "mini_task"
    assert result.duration_ms >= 0


def test_run_failed_when_test_exits_nonzero(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["exit 1"])
    result = run_task(task_yaml)
    assert result.status == "failed"
    assert result.score == 0.0


def test_run_error_when_setup_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["exit 1"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)
    assert result.status == "error"
    assert result.score == 0.0


def test_run_timeout_on_slow_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = tmp_path / "task.yaml"
    task_yaml.write_text(
        f"""
id: slow_task
name: Slow Task
repo_path: {repo}
prompt: Wait forever.
setup_commands:
  - sleep 5
test_commands:
  - "/usr/bin/true"
timeout_seconds: 1
"""
    )
    result = run_task(task_yaml)
    assert result.status == "timeout"
    assert result.score == 0.0


def test_run_error_when_repo_missing(tmp_path: Path) -> None:
    task_yaml = _write_task(
        tmp_path,
        tmp_path / "missing_repo",
        setup=["/usr/bin/true"],
        tests=["/usr/bin/true"],
    )
    result = run_task(task_yaml)
    assert result.status == "error"
    assert "repo_path does not exist" in result.stderr


def test_run_result_serializes_to_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)
    payload = json.loads(json.dumps(result.to_dict()))
    assert set(payload) == {
        "task_id",
        "status",
        "score",
        "stdout",
        "stderr",
        "duration_ms",
        "trace",
    }
    assert isinstance(payload["trace"], list)


@pytest.mark.integration
def test_starter_slugify_task_fails_initially() -> None:
    result = run_task(STARTER_TASK)
    assert result.task_id == "fix_slugify_unicode"
    assert result.status == "failed"
    assert result.score == 0.0
