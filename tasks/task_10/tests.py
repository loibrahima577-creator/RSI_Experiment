from solution import parse_csv_line

assert parse_csv_line("a,b,c") == ["a", "b", "c"]
assert parse_csv_line('a,"b,c",d') == ["a", "b,c", "d"]
assert parse_csv_line('"say ""hi"""') == ['say "hi"']
assert parse_csv_line("") == [""]
assert parse_csv_line("a,,c") == ["a", "", "c"]
assert parse_csv_line('"",x') == ["", "x"]
try:
    parse_csv_line('"unfinished')
except ValueError:
    pass
else:
    assert False, "unterminated quoted field must fail"
