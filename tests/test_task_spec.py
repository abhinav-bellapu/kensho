from pathlib import Path

import pytest

from kensho.task_spec import TaskSpec, load_task_spec

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_valid_task(tmp_path: Path) -> None:
    task_yaml = tmp_path / "task.yaml"
    repo = tmp_path / "repo"
    repo.mkdir()
    task_yaml.write_text(
        f"""
id: sample_task
name: Sample Task
repo_path: {repo}
prompt: Do the thing.
setup_commands:
  - echo setup
test_commands:
  - echo test
timeout_seconds: 30
"""
    )
    spec = load_task_spec(task_yaml)
    assert spec == TaskSpec(
        id="sample_task",
        name="Sample Task",
        repo_path=repo.resolve(),
        prompt="Do the thing.",
        setup_commands=["echo setup"],
        test_commands=["echo test"],
        timeout_seconds=30,
    )


def test_repo_path_resolved_relative_to_yaml(tmp_path: Path) -> None:
    repo = tmp_path / "nested" / "repo"
    repo.mkdir(parents=True)
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    task_yaml = tasks_dir / "task.yaml"
    task_yaml.write_text(
        """
id: rel_task
name: Relative Repo
repo_path: ../nested/repo
prompt: Fix it.
setup_commands:
  - ":"
test_commands:
  - ":"
timeout_seconds: 10
"""
    )
    spec = load_task_spec(task_yaml)
    assert spec.repo_path == repo.resolve()


def test_missing_required_field_raises(tmp_path: Path) -> None:
    task_yaml = tmp_path / "bad.yaml"
    task_yaml.write_text(
        """
id: incomplete
name: Incomplete
"""
    )
    with pytest.raises(ValueError, match="missing required fields"):
        load_task_spec(task_yaml)


def test_invalid_timeout_raises(tmp_path: Path) -> None:
    task_yaml = tmp_path / "bad.yaml"
    task_yaml.write_text(
        """
id: bad_timeout
name: Bad Timeout
repo_path: .
prompt: x
setup_commands:
  - ":"
test_commands:
  - ":"
timeout_seconds: 0
"""
    )
    with pytest.raises(ValueError, match="timeout_seconds"):
        load_task_spec(task_yaml)


def test_load_starter_task() -> None:
    root = Path(__file__).resolve().parents[1]
    task_yaml = root / "benchmarks/starter_python/tasks/fix_slugify_unicode.yaml"
    spec = load_task_spec(task_yaml)
    assert spec.id == "fix_slugify_unicode"
    assert spec.repo_path.name == "slugify_project"
