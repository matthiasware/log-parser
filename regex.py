import re
re_timestamp = r'time="([^"]+)"'
re_level = r"level=(info|warning|error)"
re_msg = r'msg="([^"]+)"'
re_file = r'file="([^"]*)"'
re_func = r"func=([^\s]*)"
re_kind = r"kind=([^\s]*)"

re_total = (
    re_timestamp
    + "\\s"
    + re_level
    + "\\s"
    + re_msg
    + "\\s"
    + re_file
    + "\\s"
    + re_func
    + "\\s"
    + re_kind
    + "\\s?"
)

regex = re.compile(re_total)
