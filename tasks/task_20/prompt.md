# Task 20: connected_components

Implement `connected_components(n, edges)` for an undirected graph with vertices numbered `0` through `n - 1`. `edges` is a sequence of endpoint pairs. Return a list of components, with each component's vertex numbers in ascending order and components ordered by their smallest vertex. Include isolated vertices. Assume endpoints are valid.

Examples:
- `connected_components(5, [(0, 1), (1, 2), (3, 4)]) == [[0, 1, 2], [3, 4]]`
- `connected_components(3, []) == [[0], [1], [2]]`
