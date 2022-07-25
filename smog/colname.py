import time
from datetime import datetime as DateTime


DATERANGE = "%d"


def build_timed_collection_name(templ, first, last):

    if templ.find(DATERANGE) < 0:
        return templ

    if first > last:
        raise Exception("first day after last")

    tm_first = first.timetuple()
    tm_last = last.timetuple()

    fst = time.strftime("%Y%m%d", tm_first)
    lst = ""

    fmt = ""
    if tm_first.tm_year != tm_last.tm_year:
        fmt += "%Y"
    if tm_first.tm_mon != tm_last.tm_mon:
        fmt += "%m"
    if tm_first.tm_mday != tm_last.tm_mday:
        fmt += "%d"
    if len(fmt) > 0:
        fmt = "-" + time.strftime(fmt, tm_last)

    fst = fst + fmt
    return templ.replace(DATERANGE, fst)
