import time
from datetime import datetime as DateTime
import re

try:
    from .file import FileStat
except:
    from file import FileStat


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


def _get_last_folder(fnam):
    f = FileStat(fnam).read_stat()
    if f.is_file():
        fnam = f.dirname()
    return FileStat(fnam).basename()


# build a proposal based on the last folder name
# strips away date prefix if present

_regex = re.compile(r"(^[0-9. -]+[\s-])(.*)")


def _strip_date_prefix(fnam):
    match = _regex.match(fnam)
    return match


def build_collection_name_proposal(fnam):
    f = _get_last_folder(fnam)
    m = _strip_date_prefix(f)
    if m:
        return m.group(2)
