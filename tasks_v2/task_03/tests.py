from solution import rotate_items

assert rotate_items([1, 2, 3, 4], 1) == (4, 1, 2, 3)
assert rotate_items([1, 2, 3], 0) == (1, 2, 3)
assert rotate_items([1, 2, 3], 3) == (1, 2, 3)
source = [1, 2, 3]
rotate_items(source, 1)
assert source == [1, 2, 3]
for bad_k in (-1, None, "2"):
    try:
        rotate_items([1, 2], bad_k)
    except ValueError:
        pass
    else:
        assert False, "invalid rotation amount must fail"
