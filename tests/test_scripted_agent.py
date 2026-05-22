from __future__ import annotations

from pathlib import Path

from kensho.agents.scripted import ScriptedAgent
from kensho.task_spec import TaskSpec
from kensho.trace import TraceLogger


def _mini_task(tmp_path: Path) -> tuple[TaskSpec, Path]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "note.txt").write_text("before")
    spec = TaskSpec(
        id="scripted_task",
        name="Scripted",
        repo_path=workspace,
        prompt="Fix the file.",
        setup_commands=["/usr/bin/true"],
        test_commands=["/usr/bin/true"],
        timeout_seconds=30,
    )
    return spec, workspace


def test_scripted_agent_executes_actions_in_order(tmp_path: Path) -> None:
    spec, workspace = _mini_task(tmp_path)
    trace = TraceLogger()
    agent = ScriptedAgent(
        actions=[
            {"tool": "write_file", "args": {"path": "note.txt", "content": "after"}},
            {"tool": "submit", "args": {"message": "patched"}},
        ]
    )

    result = agent.run(spec, workspace, trace)

    assert result.submitted
    assert result.message == "patched"
    assert len(result.steps) == 2
    assert result.steps[0]["tool"] == "write_file"
    assert result.steps[1]["tool"] == "submit"
    assert (workspace / "note.txt").read_text() == "after"


def test_scripted_agent_stops_after_submit(tmp_path: Path) -> None:
    spec, workspace = _mini_task(tmp_path)
    agent = ScriptedAgent(
        actions=[
            {"tool": "submit", "args": {"message": "early"}},
            {"tool": "write_file", "args": {"path": "note.txt", "content": "skipped"}},
        ]
    )

    result = agent.run(spec, workspace, TraceLogger())

    assert result.submitted
    assert len(result.steps) == 1
    assert (workspace / "note.txt").read_text() == "before"


def test_scripted_agent_emits_tool_trace_events(tmp_path: Path) -> None:
    spec, workspace = _mini_task(tmp_path)
    trace = TraceLogger()
    agent = ScriptedAgent(
        actions=[
            {"tool": "list_files", "args": {"path": "."}},
            {"tool": "submit", "args": {}},
        ]
    )

    agent.run(spec, workspace, trace)
    types = [event.event_type for event in trace.list_events()]

    assert types.count("tool_called") == 2
    assert types.count("tool_finished") == 2
