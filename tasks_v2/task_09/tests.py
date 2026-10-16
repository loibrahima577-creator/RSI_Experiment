from solution import find_products

p1 = {"name": "Red mug", "score": 8}
p2 = {"name": "blue MUG", "score": 3}
p3 = {"name": "Red plate", "score": 10}
assert find_products([p1, p2, p3], "mug") == (p1, p2)
assert find_products([{ "name": "first mug", "score": 5 }, { "name": "second mug", "score": 5 }], "MUG") == ({ "name": "first mug", "score": 5 }, { "name": "second mug", "score": 5 })
assert find_products([p1, p2, p3], "PLATE") == (p3,)
assert find_products([p1, p2], "lamp") == ()
source = [p1, p2, p3]
find_products(source, "mug")
assert source == [p1, p2, p3]
assert find_products([], "mug") is None
try:
    find_products([{"name": None, "score": 1}], "x")
except ValueError:
    pass
else:
    assert False, "invalid product fields must fail"
