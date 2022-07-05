def findblank(s):
    p1 = s.find(" ")
    p2 = s.find("\t")
    p = max(p1, p2)
    return p


def split_strip(s, p):
    if p < 0:
        return s.strip(), ""
    return s[:p].strip(), s[p:].strip()


def startswith_and_split(s, cmp):
    s = s.strip()
    p = findblank(s)
    h, t = split_strip(s, p)
    return h == cmp, h, t


def is_commented(s):
    if len(s) > 0:
        return s[0] in ["-", "#"]
    return False
