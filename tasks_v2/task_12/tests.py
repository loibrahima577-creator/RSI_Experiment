from solution import parse_integer_fields

assert parse_integer_fields(["12", "-4"]) == (12, -4)
assert parse_integer_fields(["007"]) == (7,)
assert parse_integer_fields([]) is None
fields = ["1", "2"]
parse_integer_fields(fields)
assert fields == ["1", "2"]
for fields in (["3", "x"], [None], 5):
    try:
        parse_integer_fields(fields)
    except ValueError:
        pass
    else:
        assert False, "invalid integer fields must fail"
