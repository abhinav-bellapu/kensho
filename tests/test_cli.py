from __future__ import annotations

import json
from pathlib import Path

import pytest

from kensho.cli import main

ROOT = Path(__file__).resolve().parents[1]
STARTER_TASK = ROOT / "benchmarks/starter_python/tasks/fix_slugify_unicode.yaml"
EXAMPLE_SCRIPT = ROOT / "examples/scripts/fix_slugify_unicode.json"


def test_cli_run_without_agent_fails_slugify(capsys) -> None:
    exit_code = main(["run", str(STARTER_TASK)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "failed"
    assert payload["score"] == 0.0
    assert "agent" not in payload


@pytest.mark.integration
def test_cli_run_scripted_passes_slugify(capsys) -> None:
    exit_code = main(["run-scripted", str(STARTER_TASK), str(EXAMPLE_SCRIPT)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "passed"
    assert payload["score"] == 1.0
    assert payload["agent"]["submitted"] is True
    assert "trace" in payload
    trace_types = [event["event_type"] for event in payload["trace"]]
    assert "agent_started" in trace_types
    assert "tool_called" in trace_types
