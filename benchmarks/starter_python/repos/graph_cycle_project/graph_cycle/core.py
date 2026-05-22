"""Cycle detection for directed graphs."""

from typing import Hashable


def has_cycle(graph: dict[Hashable, list[Hashable]]) -> bool:
    """Return True if the directed graph contains a cycle."""
    visited: set[Hashable] = set()

    def dfs(node: Hashable) -> bool:
        if node in visited:
            return True
        visited.add(node)
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        return False

    # Bug: visited is never cleared on unwind, so shared nodes look like back-edges
    for start in graph:
        if start not in visited:
            if dfs(start):
                return True
    return False
