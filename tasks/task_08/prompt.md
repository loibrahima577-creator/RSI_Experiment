# Task 08: parse_key_value

Implement `parse_key_value(text)`. Read lines in `key=value` form, trimming whitespace around keys and values. Ignore blank lines and lines whose first non-whitespace character is `#`. Split at the first `=` only. Later entries replace earlier entries with the same key. Lines without `=` are ignored.

Examples:
- `parse_key_value("a = 1\\nb=two=three") == {"a": "1", "b": "two=three"}`
- `parse_key_value("# note\\nx=ok") == {"x": "ok"}`
