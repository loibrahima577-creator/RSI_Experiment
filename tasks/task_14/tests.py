from solution import format_phone

assert format_phone("4155552671") == "(415) 555-2671"
assert format_phone("0000000000") == "(000) 000-0000"
assert format_phone("1234567890") == "(123) 456-7890"
for invalid in ("123", "12345678901", "415-555-2671", "415555267x", " 4155552671"):
    try:
        format_phone(invalid)
    except ValueError:
        pass
    else:
        assert False, "invalid phone input must fail"
