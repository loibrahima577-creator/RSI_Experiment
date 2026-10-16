# Task 10: parse_csv_line

Implement `parse_csv_line(line)` for one CSV record. Fields are comma-separated. A field may be wrapped in double quotes; inside a quoted field, a doubled quote (`""`) represents one literal quote. Commas inside quoted fields are data. Return the field strings without surrounding quotes. Raise `ValueError` for an unterminated quoted field or unexpected characters after a closing quote. An empty line represents one empty field.

Examples:
- `parse_csv_line('a,"b,c",d') == ["a", "b,c", "d"]`
- `parse_csv_line('"say ""hi"""') == ['say "hi"']`
