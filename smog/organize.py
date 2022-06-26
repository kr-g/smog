import os
import stat
import time


from datetime import datetime, date
from datetime import time as dt_time

from .file import FileStat


def build_timed_path_fnam(dt, fnam):

    dest_dir = os.path.join(
        f"{dt.year:04}",
        f"{dt.month:02}",
        f"{dt.year:04}{dt.month:02}{dt.day:02}",
        fnam,
    )

    return dest_dir


def organize_move_pic(media, repo=None):

    if repo == None:
        repo = "$REPO"

    src = media.file
    tm = media.date

    d = date(*tm[0:3])
    t = dt_time(*tm[3:6])
    dt = datetime.combine(d, t)

    fnam = src.basename()
    destfnam = build_timed_path_fnam(dt, fnam)

    dest = FileStat(repo).join([destfnam])

    clash = dest.exists()

    return src, dest, clash, tm
