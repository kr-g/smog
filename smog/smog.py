import sys
import os
import time

import argparse

from .file import FileStat
from .movepic import move_pics


def get_default_pic_folder():
    flds = ["~/Bilder", "~/Pictures"]
    for d in flds:
        f = FileStat(d, prefetch=True)
        if f.is_dir():
            return f.name
    return FileStat().name


debug = False


def main_func(mkcopy=True):

    global debug

    parser = argparse.ArgumentParser(
        prog="smog",
        usage="python3 -m %(prog)s [options]",
        description="simple media organizer",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="show_version",
        action="store_true",
        help="show version info and exit",
        default=False,
    )
    parser.add_argument(
        "-debug",
        "-d",
        dest="debug",
        action="store_true",
        help="display debug info (default: %(default)s)",
        default=debug,
    )

    base = get_default_pic_folder()

    parser.add_argument(
        "-src",
        "-scan",
        type=str,
        dest="base",
        action="store",
        metavar="INPUT_DIR",
        help="folder to scan (default: %(default)s)",
        default=base,
    )

    dest_repo = FileStat("~/media-repo")

    parser.add_argument(
        "-dest",
        "-repo",
        type=str,
        dest="dest_repo",
        action="store",
        metavar="REPO_DIR",
        help="repo folder (default: %(default)s)",
        default=dest_repo.name,
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug

    if args.show_version:
        print("Version:", VERSION)
        return

    fbase = FileStat(args.base)
    frepo = FileStat(args.dest_repo)
    if fbase.name == frepo.name:
        print("in place processing not supported")
        sys.exit(1)

    return move_pics(fbase.name, frepo, debug=args.debug)


if __name__ == "__main__":
    rc = main_func()
    print(rc)
