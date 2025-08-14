def parse_bool(value):
    return str(value).upper() in ["1", "Y", "YES", "T", "TRUE", "ON"]
