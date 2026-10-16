# Task 19: topological_order

Implement `topological_order(nodes, edges)` for a directed acyclic graph. `nodes` gives the graph's node set and `edges` contains `(source, destination)` pairs. Return an ordering in which each source precedes its destination.

Examples:
- With nodes `A, B, C` and edges `A-B, B-C`, the order is `A, B, C`.
- With no edges, every supplied node appears in the result.
