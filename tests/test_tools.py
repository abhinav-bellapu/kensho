from __future__ import annotations

from pathlib import Path

import pytest

from kensho.tools import PathTraversalError, WorkspaceTools
from kensho.trace import TraceLogger


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "hello.txt").write_text("hello")
    return root


@pytest.fixture
def tools(workspace: Path) -> WorkspaceTools:
    return WorkspaceTools(workspace, TraceLogger(), timeout_seconds=5)


def test_list_files(workspace: Path, tools: WorkspaceTools) -> None:
    result = tools.list_files(".")
    assert result.success
    assert result.data is not None
    assert "src/" in result.data["entries"]


def test_read_file(workspace: Path, tools: WorkspaceTools) -> None:
    result = tools.read_file("src/hello.txt")
    assert result.success
    assert result.data["content"] == "hello"


def test_write_file(workspace: Path, tools: WorkspaceTools) -> None:
    result = tools.write_file("src/new.txt", "updated")
    assert result.success
    assert (workspace / "src" / "new.txt").read_text() == "updated"


def test_run_shell(workspace: Path, tools: WorkspaceTools) -> None:
    result = tools.run_shell("echo kensho")
    assert result.success
    assert result.data is not None
    assert "kensho" in result.data["stdout"]


def test_path_traversal_is_blocked(tools: WorkspaceTools) -> None:
    with pytest.raises(PathTraversalError):
        tools.resolve_path("../outside.txt")

    result = tools.dispatch("read_file", {"path": "../../etc/passwd"})
    assert not result.success
    assert "escapes workspace" in (result.error or "")


def test_tool_calls_emit_trace_events(workspace: Path) -> None:
    trace = TraceLogger()
    traced_tools = WorkspaceTools(workspace, trace, timeout_seconds=5)
    traced_tools.dispatch("read_file", {"path": "src/hello.txt"})

    types = [event.event_type for event in trace.list_events()]
    assert types == ["tool_called", "tool_finished"]
    assert trace.list_events()[0].payload["tool"] == "read_file"
    assert trace.list_events()[1].payload["success"] is True


def test_submit_sets_flag(tools: WorkspaceTools) -> None:
    result = tools.submit(message="done")
    assert result.success
    assert tools.submitted
    assert tools.submit_message == "done"
