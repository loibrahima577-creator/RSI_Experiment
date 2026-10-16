from solution import parse_key_value

assert parse_key_value("a = 1\nb=two=three") == {"a": "1", "b": "two=three"}
assert parse_key_value("# note\nx=ok") == {"x": "ok"}
assert parse_key_value("") == {}
assert parse_key_value("bad line\n=empty key\ny=  ") == {"": "empty key", "y": ""}
assert parse_key_value("x=old\nx=new") == {"x": "new"}
assert parse_key_value("a=1\n  # ignored\nb=2") == {"a": "1", "b": "2"}
