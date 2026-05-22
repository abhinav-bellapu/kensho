# Kensho Bench

Kensho Bench is an evaluation harness for autonomous coding agents.

Goals:
- reproducible benchmark tasks
- sandboxed execution
- tool-use tracing
- automated verification
- regression analysis

Engineering principles:
- keep changes small and testable
- use typed Python
- use pytest
- backend first
- avoid unnecessary dependencies
- do not implement frontend yet
- do not implement Docker yet
- every feature should include tests

Validation:
- pytest
- python -m kensho --help