"""Task runner: copy repo, run setup/tests, return JSON result."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kensho.task_spec import TaskSpec, load_task_spec
from kensho.trace import TraceEvent, TraceLogger

Status = str  # passed | failed | error | timeout


@dataclass
class RunResult:
    task_id: str
    status: Status
    score: float
    stdout: str
    stderr: str
    duration_ms: int
    trace: list[TraceEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "score": self.score,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "trace": [event.to_dict() for event in self.trace],
        }


def _run_command(
    command: str,
    cwd: Path,
    timeout_seconds: int,
) -> tuple[int, str, str, Status | None]:
    """Run a shell command. Returns (exit_code, stdout, stderr, timeout_status)."""
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return completed.returncode, completed.stdout, completed.stderr, None
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return -1, stdout, stderr, "timeout"


def _append_output(parts: list[str], text: str) -> None:
    if text:
        parts.append(text)


def _run_setup_command(
    trace: TraceLogger,
    command: str,
    index: int,
    workspace: Path,
    timeout_seconds: int,
    stdout_parts: list[str],
    stderr_parts: list[str],
) -> tuple[Status | None, str | None]:
    """Run one setup command with trace events. Returns (final_status, error_reason)."""
    trace.log("setup_command_started", {"command": command, "index": index})
    code, out, err, timeout_status = _run_command(command, workspace, timeout_seconds)
    _append_output(stdout_parts, out)
    _append_output(stderr_parts, err)
    trace.log(
        "setup_command_finished",
        {"command": command, "index": index, "exit_code": code},
    )
    if timeout_status == "timeout":
        trace.log("error", {"reason": "setup_timeout", "command": command, "index": index})
        return "timeout", "setup_timeout"
    if code != 0:
        trace.log(
            "error",
            {"reason": "setup_failed", "command": command, "index": index, "exit_code": code},
        )
        return "error", "setup_failed"
    return None, None


def _run_test_command(
    trace: TraceLogger,
    command: str,
    index: int,
    workspace: Path,
    timeout_seconds: int,
    stdout_parts: list[str],
    stderr_parts: list[str],
) -> tuple[bool, Status | None]:
    """Run one test command with trace events. Returns (failed, final_status)."""
    trace.log("test_command_started", {"command": command, "index": index})
    code, out, err, timeout_status = _run_command(command, workspace, timeout_seconds)
    _append_output(stdout_parts, out)
    _append_output(stderr_parts, err)
    trace.log(
        "test_command_finished",
        {"command": command, "index": index, "exit_code": code},
    )
    if timeout_status == "timeout":
        trace.log("error", {"reason": "test_timeout", "command": command, "index": index})
        return False, "timeout"
    if code != 0:
        return True, None
    return False, None


def _finish_run(
    trace: TraceLogger,
    spec: TaskSpec,
    status: Status,
    score: float,
    stdout: str,
    stderr: str,
    duration_ms: int,
) -> RunResult:
    trace.log("scorer_result", {"status": status, "score": score})
    trace.log("run_finished", {"status": status, "duration_ms": duration_ms})
    return RunResult(
        task_id=spec.id,
        status=status,
        score=score,
        stdout=stdout,
        stderr=stderr,
        duration_ms=duration_ms,
        trace=trace.list_events(),
    )


def run_task(task_yaml: Path) -> RunResult:
    """Execute a benchmark task and return structured results."""
    started = time.perf_counter()
    trace = TraceLogger()

    try:
        spec = load_task_spec(task_yaml)
        trace.log(
            "task_loaded",
            {
                "task_id": spec.id,
                "name": spec.name,
                "repo_path": str(spec.repo_path),
            },
        )

        if not spec.repo_path.is_dir():
            trace.log("error", {"reason": "repo_not_found", "repo_path": str(spec.repo_path)})
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return _finish_run(
                trace,
                spec,
                status="error",
                score=0.0,
                stdout="",
                stderr=f"repo_path does not exist: {spec.repo_path}",
                duration_ms=elapsed_ms,
            )

        stdout_parts: list[str] = []
        stderr_parts: list[str] = []

        with tempfile.TemporaryDirectory(prefix="kensho_") as tmp:
            workspace = Path(tmp) / "workspace"
            shutil.copytree(spec.repo_path, workspace)
            trace.log("workspace_created", {"workspace": str(workspace)})

            for index, command in enumerate(spec.setup_commands):
                setup_status, _ = _run_setup_command(
                    trace,
                    command,
                    index,
                    workspace,
                    spec.timeout_seconds,
                    stdout_parts,
                    stderr_parts,
                )
                if setup_status is not None:
                    elapsed_ms = int((time.perf_counter() - started) * 1000)
                    return _finish_run(
                        trace,
                        spec,
                        status=setup_status,
                        score=0.0,
                        stdout="".join(stdout_parts),
                        stderr="".join(stderr_parts),
                        duration_ms=elapsed_ms,
                    )

            test_failed = False
            for index, command in enumerate(spec.test_commands):
                failed, final_status = _run_test_command(
                    trace,
                    command,
                    index,
                    workspace,
                    spec.timeout_seconds,
                    stdout_parts,
                    stderr_parts,
                )
                if final_status == "timeout":
                    elapsed_ms = int((time.perf_counter() - started) * 1000)
                    return _finish_run(
                        trace,
                        spec,
                        status="timeout",
                        score=0.0,
                        stdout="".join(stdout_parts),
                        stderr="".join(stderr_parts),
                        duration_ms=elapsed_ms,
                    )
                if failed:
                    test_failed = True

            elapsed_ms = int((time.perf_counter() - started) * 1000)
            status: Status = "failed" if test_failed else "passed"
            score = 1.0 if status == "passed" else 0.0
            return _finish_run(
                trace,
                spec,
                status=status,
                score=score,
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                duration_ms=elapsed_ms,
            )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        trace.log("error", {"reason": "unexpected", "message": str(exc)})
        task_id = "unknown"
        try:
            task_id = load_task_spec(task_yaml).id
        except Exception:
            pass
        trace.log("scorer_result", {"status": "error", "score": 0.0})
        trace.log("run_finished", {"status": "error", "duration_ms": elapsed_ms})
        return RunResult(
            task_id=task_id,
            status="error",
            score=0.0,
            stdout="",
            stderr=str(exc),
            duration_ms=elapsed_ms,
            trace=trace.list_events(),
        )


def run_task_json(task_yaml: Path) -> str:
    """Run a task and return JSON-serialized results."""
    return json.dumps(run_task(task_yaml).to_dict(), indent=2)
