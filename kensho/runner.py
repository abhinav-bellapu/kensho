"""Task runner: copy repo, run setup/tests, return JSON result."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from kensho.task_spec import TaskSpec, load_task_spec

Status = str  # passed | failed | error | timeout


@dataclass
class RunResult:
    task_id: str
    status: Status
    score: float
    stdout: str
    stderr: str
    duration_ms: int

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "score": self.score,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
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


def _run_commands(
    commands: list[str],
    cwd: Path,
    timeout_seconds: int,
) -> tuple[Status, str, str]:
    """Run commands in sequence. Stops on first failure or timeout."""
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []

    for command in commands:
        code, out, err, timeout_status = _run_command(command, cwd, timeout_seconds)
        if out:
            stdout_parts.append(out)
        if err:
            stderr_parts.append(err)
        if timeout_status == "timeout":
            return "timeout", "".join(stdout_parts), "".join(stderr_parts)
        if code != 0:
            return "error", "".join(stdout_parts), "".join(stderr_parts)

    return "passed", "".join(stdout_parts), "".join(stderr_parts)


def run_task(task_yaml: Path) -> RunResult:
    """Execute a benchmark task and return structured results."""
    started = time.perf_counter()
    spec = load_task_spec(task_yaml)

    if not spec.repo_path.is_dir():
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return RunResult(
            task_id=spec.id,
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

        setup_status, setup_out, setup_err = _run_commands(
            spec.setup_commands,
            workspace,
            spec.timeout_seconds,
        )
        stdout_parts.append(setup_out)
        stderr_parts.append(setup_err)

        if setup_status == "timeout":
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return RunResult(
                task_id=spec.id,
                status="timeout",
                score=0.0,
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                duration_ms=elapsed_ms,
            )

        if setup_status == "error":
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return RunResult(
                task_id=spec.id,
                status="error",
                score=0.0,
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                duration_ms=elapsed_ms,
            )

        test_failed = False
        for command in spec.test_commands:
            code, out, err, timeout_status = _run_command(
                command,
                workspace,
                spec.timeout_seconds,
            )
            if out:
                stdout_parts.append(out)
            if err:
                stderr_parts.append(err)
            if timeout_status == "timeout":
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                return RunResult(
                    task_id=spec.id,
                    status="timeout",
                    score=0.0,
                    stdout="".join(stdout_parts),
                    stderr="".join(stderr_parts),
                    duration_ms=elapsed_ms,
                )
            if code != 0:
                test_failed = True

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        status: Status = "failed" if test_failed else "passed"
        score = 1.0 if status == "passed" else 0.0
        return RunResult(
            task_id=spec.id,
            status=status,
            score=score,
            stdout="".join(stdout_parts),
            stderr="".join(stderr_parts),
            duration_ms=elapsed_ms,
        )


def run_task_json(task_yaml: Path) -> str:
    """Run a task and return JSON-serialized results."""
    return json.dumps(run_task(task_yaml).to_dict(), indent=2)
