# Task 12: group_by_key

Implement `group_by_key(records, key)`. Given a list of dictionaries, return a dictionary mapping each value of `record[key]` to the list of records with that value, preserving input order within each group and the original record objects. Every record contains the requested key.

Examples:
- `group_by_key([{"team": "A", "n": 1}, {"team": "B", "n": 2}, {"team": "A", "n": 3}], "team") == {"A": [{"team": "A", "n": 1}, {"team": "A", "n": 3}], "B": [{"team": "B", "n": 2}]}`
- `group_by_key([], "kind") == {}`
