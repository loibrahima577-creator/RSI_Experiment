# Task 19: shortest_path

Implement `shortest_path(grid, start, goal)`. `grid` is a rectangular list of rows where `0` is open and `1` is blocked. `start` and `goal` are `(row, column)` pairs. Movement is allowed one cell at a time in the four cardinal directions, with every move costing one. Return a shortest path as a list of coordinate tuples including both endpoints, or `[]` if no path exists. A blocked or out-of-bounds endpoint has no path. If start equals goal and is open, return `[start]`.

Examples:
- `shortest_path([[0, 0], [1, 0]], (0, 0), (1, 1)) == [(0, 0), (0, 1), (1, 1)]`
- `shortest_path([[0, 1]], (0, 0), (0, 1)) == []`
