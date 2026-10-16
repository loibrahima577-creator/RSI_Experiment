from solution import merge_ranges

assert merge_ranges([[1, 4], [3, 7], [10, 12]]) == ((1, 7), (10, 12))
assert merge_ranges([[2, 3], [3, 5]]) == ((2, 5),)
assert merge_ranges([[8, 9], [1, 2], [4, 5]]) == ((1, 2), (4, 5), (8, 9))
assert merge_ranges([]) is None
ranges = [[4, 8], [1, 5]]
merge_ranges(ranges)
assert ranges == [[4, 8], [1, 5]]
for invalid in ([[3, 1]], [[1]], None):
    try:
        merge_ranges(invalid)
    except ValueError:
        pass
    else:
        assert False, "invalid ranges must fail"
