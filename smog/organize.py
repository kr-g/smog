import os


from datetime import datetime, date
from datetime import time as dt_time

try:
    from .file import FileStat
except:
    from file import FileStat


def build_timed_path_fnam_t(tm, fnam):
    dt = datetime.fromtimestamp(tm)
    return build_timed_path_fnam(dt, fnam)


def build_timed_path_fnam(dt, fnam):

    dest_dir = os.path.join(
        f"{dt.year:04}",
        f"{dt.month:02}",
        f"{dt.year:04}{dt.month:02}{dt.day:02}",
        fnam,
    )

    return dest_dir
