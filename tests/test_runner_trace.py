from __future__ import annotations

import json
from pathlib import Path

from kensho.runner import run_task

ROOT = Path(__file__).resolve().parents[1]
STARTER_TASK = ROOT / "benchmarks/starter_python/tasks/fix_slugify_unicode.yaml"

EXPECTED_EVENT_TYPES = {
    "task_loaded",
    "workspace_created",
    "setup_command_started",
    "setup_command_finished",
    "agent_started",
    "agent_finished",
    "tool_called",
    "tool_finished",
    "test_command_started",
    "test_command_finished",
    "scorer_result",
    "run_finished",
    "error",
}


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


def _event_types(result) -> list[str]:
    return [event.event_type for event in result.trace]


def test_trace_events_are_created_in_order(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)

    indices = [event.step_index for event in result.trace]
    assert indices == list(range(len(indices)))


def test_runner_emits_expected_trace_event_types(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)

    types = _event_types(result)
    assert types[0] == "task_loaded"
    assert "workspace_created" in types
    assert "setup_command_started" in types
    assert "setup_command_finished" in types
    assert "test_command_started" in types
    assert "test_command_finished" in types
    assert types[-2] == "scorer_result"
    assert types[-1] == "run_finished"
    assert set(types).issubset(EXPECTED_EVENT_TYPES)


def test_failed_test_commands_still_emit_useful_trace_events(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["exit 1"])
    result = run_task(task_yaml)

    types = _event_types(result)
    finished = [
        event
        for event in result.trace
        if event.event_type == "test_command_finished"
    ]
    assert result.status == "failed"
    assert "test_command_started" in types
    assert "test_command_finished" in types
    assert finished[-1].payload["exit_code"] == 1
    assert "error" not in types
    assert types[-2] == "scorer_result"
    assert types[-1] == "run_finished"


def test_setup_failure_emits_error_trace_event(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["exit 1"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)

    error_events = [event for event in result.trace if event.event_type == "error"]
    assert result.status == "error"
    assert len(error_events) == 1
    assert error_events[0].payload["reason"] == "setup_failed"
    assert "test_command_started" not in _event_types(result)


def test_json_output_includes_trace_events(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml = _write_task(tmp_path, repo, setup=["/usr/bin/true"], tests=["/usr/bin/true"])
    result = run_task(task_yaml)

    payload = json.loads(json.dumps(result.to_dict()))
    assert "trace" in payload
    assert isinstance(payload["trace"], list)
    assert payload["trace"][0]["event_type"] == "task_loaded"
    assert set(payload["trace"][0]) == {"step_index", "event_type", "timestamp", "payload"}


def test_starter_task_trace_includes_test_command_events() -> None:
    result = run_task(STARTER_TASK)
    types = _event_types(result)
    assert "task_loaded" in types
    assert "workspace_created" in types
    assert types.count("setup_command_started") >= 1
    assert types.count("test_command_finished") >= 1
    assert "scorer_result" in types
    assert "run_finished" in types
