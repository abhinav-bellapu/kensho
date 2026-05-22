from __future__ import annotations

import json
from pathlib import Path

import pytest

from kensho.script_loader import load_script

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_SCRIPT = ROOT / "examples/scripts/fix_slugify_unicode.json"


def test_load_valid_script_json() -> None:
    actions = load_script(EXAMPLE_SCRIPT)
    assert len(actions) == 3
    assert actions[0]["tool"] == "read_file"
    assert actions[0]["args"]["path"] == "slugify/core.py"
    assert actions[2]["tool"] == "submit"


def test_reject_non_list_json(tmp_path: Path) -> None:
    script = tmp_path / "bad.json"
    script.write_text(json.dumps({"tool": "submit"}))
    with pytest.raises(ValueError, match="list of actions"):
        load_script(script)


def test_reject_action_missing_tool(tmp_path: Path) -> None:
    script = tmp_path / "bad.json"
    script.write_text(json.dumps([{"args": {}}]))
    with pytest.raises(ValueError, match="tool"):
        load_script(script)


def test_default_missing_args_to_empty_dict(tmp_path: Path) -> None:
    script = tmp_path / "ok.json"
    script.write_text(json.dumps([{"tool": "submit"}]))
    actions = load_script(script)
    assert actions == [{"tool": "submit", "args": {}}]
