from solution import group_by_key

rows = [{"team": "A", "n": 1}, {"team": "B", "n": 2}, {"team": "A", "n": 3}]
assert group_by_key(rows, "team") == {"A": [rows[0], rows[2]], "B": [rows[1]]}
assert group_by_key([], "kind") == {}
assert group_by_key([{"x": 1}, {"x": 1}], "x") == {1: [{"x": 1}, {"x": 1}]}
assert group_by_key([{"x": None}, {"x": 0}], "x") == {None: [{"x": None}], 0: [{"x": 0}]}
groups = group_by_key(rows, "team")
assert groups["A"][0] is rows[0]
