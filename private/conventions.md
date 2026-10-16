# v2 House Conventions

1. Functions never mutate input arguments.
2. Invalid input, including wrong types, `None`, or prohibited negative values, raises `ValueError`.
3. Collection results use tuples, never lists (nested collections use nested tuples).
4. String comparisons are case-insensitive.
5. Empty input returns `None`.
6. Ties preserve original input order.
