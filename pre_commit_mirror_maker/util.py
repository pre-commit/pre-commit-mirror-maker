def from_utf8(s):
    if type(s) is bytes:
        return s.decode('utf-8')
    else:
        return s
