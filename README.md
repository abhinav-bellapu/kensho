# Kensho Bench

Kensho Bench is a **local, zero-cost** evaluation harness for autonomous coding agents. It runs benchmark tasks in isolated workspaces, records structured traces, scores results with pytest, and supports deterministic scripted agents before any hosted LLM APIs are added.

## Local-first / zero-cost

- No OpenAI, Anthropic, or other paid API calls
- No API keys required
- No Docker, database, or frontend in this milestone
- Runs entirely on your machine with Python 3.10+

## Install

```bash
pip install -e ".[dev]"
# or for a quick run:
pip install PyYAML pytest
export PYTHONPATH=.
```

## Run a benchmark (no agent)

Runs setup commands, then test commands, and prints JSON with `status`, `score`, `trace`, and output:

```bash
python -m kensho run benchmarks/starter_python/tasks/fix_slugify_unicode.yaml
```

The starter slugify task is intentionally buggy and should return `"status": "failed"` until fixed.

## Run with a scripted agent

Provide a JSON file listing tool actions. Kensho runs setup, executes the scripted agent, then runs tests:

```bash
python -m kensho run-scripted \
  benchmarks/starter_python/tasks/fix_slugify_unicode.yaml \
  examples/scripts/fix_slugify_unicode.json
```

A successful fix should return `"status": "passed"` and an `agent` block describing submitted steps.

## Scripted agent JSON format

The script file is a JSON **array** of actions. Each action has:

- `tool` (string, required): one of `list_files`, `read_file`, `write_file`, `run_shell`, `submit`
- `args` (object, optional): tool arguments; defaults to `{}`

Example:

```json
[
  {"tool": "read_file", "args": {"path": "slugify/core.py"}},
  {"tool": "write_file", "args": {"path": "slugify/core.py", "content": "..."}},
  {"tool": "submit", "args": {"message": "Fixed Unicode slugification."}}
]
```

Scripted agents are **deterministic**: the same script and task always produce the same tool sequence. They are useful for regression tests, CI, and debugging the harness before wiring in real LLM agents.

## Validate

```bash
PYTHONPATH=. pytest -v
PYTHONPATH=. python3 -m kensho --help
```
