from solution import parse_duration

assert parse_duration("1:02:03") == 3723
assert parse_duration("0:00:09") == 9
assert parse_duration("12:59:59") == 46799
assert parse_duration("0:0:0") == 0
for invalid in ("1:60:00", "-1:00:00"):
    try:
        parse_duration(invalid)
    except ValueError:
        pass
    else:
        assert False, "invalid duration must fail"
