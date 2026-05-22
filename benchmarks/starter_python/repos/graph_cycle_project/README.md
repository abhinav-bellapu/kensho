# Graph cycle detection benchmark

`has_cycle(graph)` detects whether a directed graph (adjacency list) contains a cycle.

**Intentional bug:** DFS marks nodes in a single global `visited` set and never tracks the current path/recursion stack, so DAGs with reconverging paths are reported as cyclic.
