"""Safe workspace-scoped tools for agents."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kensho.trace import TraceLogger


class PathTraversalError(ValueError):
    """Raised when a tool path escapes the workspace."""


@dataclass
class ToolResult:
    success: bool
    tool: str
    data: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "tool": self.tool,
            "data": self.data,
            "error": self.error,
        }


class WorkspaceTools:
    """Tools that operate only inside a sandboxed workspace directory."""

    def __init__(
        self,
        workspace: Path,
        trace: TraceLogger,
        timeout_seconds: int,
    ) -> None:
        self._workspace = workspace.resolve()
        self._trace = trace
        self._timeout_seconds = timeout_seconds
        self.submitted = False
        self.submit_message = ""

    def resolve_path(self, path: str) -> Path:
        if not path or not isinstance(path, str):
            raise ValueError("path must be a non-empty string")
        target = (self._workspace / path).resolve()
        try:
            target.relative_to(self._workspace)
        except ValueError as exc:
            raise PathTraversalError(f"path escapes workspace: {path}") from exc
        return target

    def dispatch(self, tool: str, args: dict[str, Any] | None = None) -> ToolResult:
        args = dict(args or {})
        self._trace.log("tool_called", {"tool": tool, "arguments": args})

        try:
            if tool == "list_files":
                result = self.list_files(path=args.get("path", "."))
            elif tool == "read_file":
                result = self.read_file(path=args["path"])
            elif tool == "write_file":
                result = self.write_file(path=args["path"], content=args["content"])
            elif tool == "run_shell":
                result = self.run_shell(command=args["command"])
            elif tool == "submit":
                result = self.submit(message=args.get("message", ""))
            else:
                result = ToolResult(
                    success=False,
                    tool=tool,
                    error=f"unknown tool: {tool}",
                )
        except KeyError as exc:
            result = ToolResult(success=False, tool=tool, error=f"missing argument: {exc}")
        except PathTraversalError as exc:
            result = ToolResult(success=False, tool=tool, error=str(exc))
        except ValueError as exc:
            result = ToolResult(success=False, tool=tool, error=str(exc))
        except OSError as exc:
            result = ToolResult(success=False, tool=tool, error=str(exc))

        self._trace.log(
            "tool_finished",
            {"tool": tool, "success": result.success, "error": result.error},
        )
        return result

    def list_files(self, path: str = ".") -> ToolResult:
        try:
            target = self.resolve_path(path)
        except (PathTraversalError, ValueError) as exc:
            return ToolResult(success=False, tool="list_files", error=str(exc))
        if not target.exists():
            return ToolResult(success=False, tool="list_files", error="path does not exist")
        if not target.is_dir():
            return ToolResult(success=False, tool="list_files", error="path is not a directory")

        entries = sorted(
            item.name + ("/" if item.is_dir() else "")
            for item in target.iterdir()
        )
        return ToolResult(
            success=True,
            tool="list_files",
            data={"path": path, "entries": entries},
        )

    def read_file(self, path: str) -> ToolResult:
        try:
            target = self.resolve_path(path)
        except (PathTraversalError, ValueError) as exc:
            return ToolResult(success=False, tool="read_file", error=str(exc))
        if not target.is_file():
            return ToolResult(success=False, tool="read_file", error="file does not exist")
        content = target.read_text()
        return ToolResult(
            success=True,
            tool="read_file",
            data={"path": path, "content": content},
        )

    def write_file(self, path: str, content: str) -> ToolResult:
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        try:
            target = self.resolve_path(path)
        except (PathTraversalError, ValueError) as exc:
            return ToolResult(success=False, tool="write_file", error=str(exc))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return ToolResult(
            success=True,
            tool="write_file",
            data={"path": path, "bytes_written": len(content.encode())},
        )

    def run_shell(self, command: str) -> ToolResult:
        if not command or not isinstance(command, str):
            raise ValueError("command must be a non-empty string")
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
            )
            return ToolResult(
                success=completed.returncode == 0,
                tool="run_shell",
                data={
                    "command": command,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
                error=None if completed.returncode == 0 else "non-zero exit code",
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                tool="run_shell",
                error="command timed out",
            )

    def submit(self, message: str = "") -> ToolResult:
        self.submitted = True
        self.submit_message = message
        return ToolResult(
            success=True,
            tool="submit",
            data={"message": message},
        )
