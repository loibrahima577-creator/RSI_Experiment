from solution import nearest_date

assert nearest_date(["2024-01-01", "2024-01-09"], "2024-01-08") == "2024-01-09"
assert nearest_date(["2020-02-29"], "2020-03-01") == "2020-02-29"
assert nearest_date(["2024-01-01", "2024-01-03"], "2024-01-02") == "2024-01-01"
assert nearest_date([], "2024-01-01") is None
dates = ["2024-01-03", "2024-01-01"]
nearest_date(dates, "2024-01-02")
assert dates == ["2024-01-03", "2024-01-01"]
try:
    nearest_date(["2024-02-30"], "2024-01-01")
except ValueError:
    pass
else:
    assert False, "invalid dates must fail"
