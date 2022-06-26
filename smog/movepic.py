import time

from .examine import i_examine_pic as examine_pic
from .organize import organize_move_pic


def move_pics(base, dest_repo, mkcopy=True, debug=True):

    no_files = 0

    for media in examine_pic(base, recursive=True):

        no_files = no_files + 1

        src, dest, clash, tm = organize_move_pic(media, repo=dest_repo.name)

        debug and print(
            src.name,
            dest.name,
            "exif_date",
            media.exif_date,
            "guess_date",
            media.guess_date,
            "clash",
            clash,
        )

        tm = time.mktime(tm)

        if not clash:
            s, d = src.move(dest.name, dryrun=not True, mkcopy=mkcopy)
            if mkcopy:
                dest.touch_ux((tm, tm))
        else:
            same = src.hash() == dest.hash()
            if not same:
                debug and print(
                    "---exists-as-different---no-copy---",
                    src.name,
                    dest.name,
                )

    return no_files
