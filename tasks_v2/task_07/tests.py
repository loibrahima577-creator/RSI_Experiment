from solution import common_suffix

assert common_suffix(["walking", "talking"]) == "alking"
assert common_suffix(["Dog", "fog"]) == "og"
assert common_suffix(["cat", "dog"]) == ""
assert common_suffix([]) is None
assert common_suffix(["same", "same"]) == "same"
