from solution import days_between

assert days_between("2024-01-01", "2024-01-04") == 3
assert days_between("2024-03-01", "2024-02-28") == 2
assert days_between("2020-02-28", "2020-03-01") == 2
assert days_between("2023-12-31", "2024-01-01") == 1
assert days_between("1999-05-10", "1999-05-10") == 0
assert days_between("2022-04-01", "2022-03-01") == 31
