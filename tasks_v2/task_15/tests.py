from solution import median_value

assert median_value([9, 1, 5]) == 5
assert median_value([2, 8]) == 5
assert median_value([4]) == 4
assert median_value([]) is None
values = [9, 1, 5]
median_value(values)
assert values == [9, 1, 5]
for invalid in ([1, "2"], None, "not-a-sequence"):
    try:
        median_value(invalid)
    except ValueError:
        pass
    else:
        assert False, "invalid measurements must fail"
