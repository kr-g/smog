import os
import time

from .file import FileStat
from .timeguess import tm_guess_from_fnam

from .exif import parse_exif_date, exif_tags, get_original_date_time

from .media import Media


def ifile(
    fpath,
    ext=None,
    recursive=False,
):

    fbase = FileStat(fpath)

    if ext != None and len(ext) > 0:
        ext = list(map(lambda x: "." + x.upper(), ext))
    else:
        ext = None

    for f in fbase.iglob(recursive=recursive, prefetch=True):

        if not f.is_file():
            continue

        _, fext = f.splitext()

        if ext:
            try:
                _ = ext.index(fext.upper())
            except:
                # ext not found
                continue

        yield f


def set_tm_data(r, tm, guess_date=False):
    r["date"] = tm
    r["guess_date"] = guess_date
    r["norm_date"] = time.strftime("%Y%m%d", tm)
    r["norm_time"] = time.strftime("%H%M%S", tm)


def i_examine_pic(
    fpath,
    recursive=False,
):

    files = ifile(
        fpath,
        [
            "jpg",
            "jpeg",
            "jpe",
            "jfif",
            "tif",
            "tiff",
            "png",
        ],
        recursive=recursive,
    )

    for f in files:

        r = {}

        r["file"] = f
        r["exif_date"] = False

        # first modification date
        ftime = f.ftime()
        set_tm_data(r, ftime)

        _raw, tag_data, _missing = exif_tags(f.name)

        if _raw:
            r["exif"] = tag_data

            try:
                exif_date = get_original_date_time(tag_data)
                set_tm_data(r, exif_date)
                r["exif_date"] = True

                yield Media(r)

                continue

            except Exception as ex:
                pass

        # no exif or missing data time

        gtime = tm_guess_from_fnam(f.name)
        if gtime:
            set_tm_data(r, gtime, guess_date=gtime is not None)

        yield Media(r)
