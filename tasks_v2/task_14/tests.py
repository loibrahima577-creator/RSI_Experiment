from solution import sort_events

early = {"time": "2023-01-01T09:00:00", "name": "early"}
late = {"time": "2023-01-02T09:00:00", "name": "late"}
same_a = {"time": "2023-01-03T10:00:00", "name": "A"}
same_b = {"time": "2023-01-03T10:00:00", "name": "B"}
assert sort_events([late, early]) == (early, late)
assert sort_events([same_a, same_b]) == (same_a, same_b)
assert sort_events([]) is None
source = [late, early]
sort_events(source)
assert source == [late, early]
try:
    sort_events([{"time": "yesterday"}])
except ValueError:
    pass
else:
    assert False, "invalid event time must fail"
