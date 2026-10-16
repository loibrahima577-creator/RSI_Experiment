# Task 16: merge_intervals

Implement `merge_intervals(intervals)`. Each interval is a pair `[start, end]` with `start <= end`. Return sorted intervals, merging any intervals that overlap or touch at an endpoint. The result uses fresh two-element lists. Empty input returns an empty list.

Examples:
- `merge_intervals([[1, 3], [2, 5], [8, 9]]) == [[1, 5], [8, 9]]`
- `merge_intervals([[1, 2], [2, 4]]) == [[1, 4]]`
