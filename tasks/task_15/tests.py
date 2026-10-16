from solution import sort_records

a = {"priority": 1, "name": "Zed"}
b = {"priority": 2, "name": "amy"}
c = {"priority": 2, "name": "Bob"}
assert sort_records([a, b, c]) == [b, c, a]
assert sort_records([]) == []
assert sort_records([{"priority": 3, "name": "al"}, {"priority": 3, "name": "AL"}]) == [{"priority": 3, "name": "AL"}, {"priority": 3, "name": "al"}]
assert sort_records([{"priority": 1, "name": "x"}, {"priority": 2, "name": "z"}]) == [{"priority": 2, "name": "z"}, {"priority": 1, "name": "x"}]
source = [a, b]
sort_records(source)
assert source == [a, b]
