from __future__ import annotations

from pathlib import Path

import pytest

from kensho.agents.scripted import ScriptedAgent
from kensho.runner import run_task

ROOT = Path(__file__).resolve().parents[1]
STARTER_TASK = ROOT / "benchmarks/starter_python/tasks/fix_slugify_unicode.yaml"

FIXED_SLUGIFY_CORE = '''"""Convert text to URL-friendly slugs."""

import unicodedata


def slugify(text: str) -> str:
    """Return a lowercase slug with spaces replaced by hyphens."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", errors="ignore").decode("ascii")
    return "-".join(ascii_text.lower().strip().split())
'''


def slugify_fix_actions() -> list[dict]:
    return [
        {"tool": "read_file", "args": {"path": "slugify/core.py"}},
        {
            "tool": "write_file",
            "args": {"path": "slugify/core.py", "content": FIXED_SLUGIFY_CORE},
        },
        {"tool": "submit", "args": {"message": "Transliterate unicode before slugifying."}},
    ]


@pytest.mark.integration
def test_scripted_agent_fixes_slugify_benchmark() -> None:
    result = run_task(STARTER_TASK, agent=ScriptedAgent(slugify_fix_actions()))

    assert result.agent is not None
    assert result.agent.submitted
    assert result.status == "passed"
    assert result.score == 1.0

    trace_types = [event.event_type for event in result.trace]
    assert "agent_started" in trace_types
    assert "agent_finished" in trace_types
    assert "tool_called" in trace_types
    assert trace_types.count("tool_finished") >= 3
