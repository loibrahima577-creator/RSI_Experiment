from solution import parse_clock

assert parse_clock("12:30 PM") == 750
assert parse_clock("1:05 AM") == 65
assert parse_clock("12:00 AM") == 0
assert parse_clock("11:59 pM") == 1439
assert parse_clock("") is None
for value in ("13:00 PM", "2:60 AM", "noon"):
    try:
        parse_clock(value)
    except ValueError:
        pass
    else:
        assert False, "malformed clock text must fail"
