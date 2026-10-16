# Task 11: parse_duration

Implement `parse_duration(text)`. Parse exactly three colon-separated, nonnegative integer fields in `hours:minutes:seconds` form and return total seconds. Minutes and seconds must each be from 0 through 59. Hours may be any nonnegative integer. Raise `ValueError` for malformed input or out-of-range fields.

Examples:
- `parse_duration("1:02:03") == 3723`
- `parse_duration("0:00:09") == 9`
