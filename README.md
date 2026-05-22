# Kensho Bench

Kensho Bench is a **local, zero-cost** evaluation harness for autonomous coding agents. It runs benchmark tasks in isolated workspaces, records structured traces, scores results with pytest, and supports deterministic scripted agents before any hosted LLM APIs are added.

## Local-first / zero-cost

- No OpenAI, Anthropic, or other paid API calls
- No API keys required
- No Docker, database, or frontend in this milestone
- Runs entirely on your machine with Python 3.10+

## Starter benchmark suite

Under `benchmarks/starter_python/` you will find **intentionally broken** mini Python repos and matching task YAML files. Each task copies a repo into a sandbox, runs setup, optionally runs an agent, then scores with pytest. Without an agent, every starter task should return `"status": "failed"`.

| Task ID | What the bug exercises |
|---------|-------------------------|
| `fix_slugify_unicode` | Unicode transliteration vs stripping non-ASCII |
| `fix_binary_search_off_by_one` | Binary search loop boundary (`left < right`) |
| `fix_lru_cache_eviction` | LRU eviction order (wrong end of recency list) |
| `fix_markdown_link_parser` | Parsing multiple / adjacent markdown links |
| `fix_rate_limiter_boundary` | Fixed-window rate limit at timestamp boundaries |
| `fix_graph_cycle_detection` | DFS cycle detection vs DAG reconvergence |

Each repo includes a `README.md` describing expected behavior and the deliberate defect.

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
python -m kensho run benchmarks/starter_python/tasks/fix_binary_search_off_by_one.yaml
```

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
