# Task 15: sort_records

Implement `sort_records(records)`. Each record is a dictionary with integer `priority` and string `name`. Return a new list sorted by descending priority, then ascending case-insensitive name, then ascending original name as a deterministic tie-breaker. Do not mutate the input.

Examples:
- `sort_records([{"priority": 1, "name": "Zed"}, {"priority": 2, "name": "amy"}])` puts `amy` first.
- Names `"AL"` and `"al"` at equal priority sort as `"AL"` then `"al"`.
