import os
import time
from datetime import datetime as DateTime

try:
    from .file import FileStat
except:
    from file import FileStat


def build_timed_path_fnam_t(tm, fnam):
    dt = DateTime.fromtimestamp(tm)
    return build_timed_path_fnam(dt, fnam)


def build_timed_path_fnam(dt, fnam):

    dest_dir = os.path.join(
        f"{dt.year:04}",
        f"{dt.month:02}",
        f"{dt.year:04}{dt.month:02}{dt.day:02}",
        fnam,
    )

    return dest_dir


def make_timed_rel_store_path(prefix="proc-media", incl_tm=False):
    tm = time.strftime(
        "%Y-%m-%d" + (" %H:%M" if incl_tm else ""), time.localtime(time.time())
    )
    store = f"{prefix} {tm}"
    return store
