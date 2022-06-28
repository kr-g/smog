import sys
import os
import time

import json
import argparse

from .file import FileStat
from .movepic import move_pics

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import xmp_dict, cleanup_xmp_dict, xmp_tags

VERSION = "v0.0.2-a"


def get_default_pic_folder():
    flds = ["~/Bilder", "~/Pictures"]
    for d in flds:
        f = FileStat(d, prefetch=True)
        if f.is_dir():
            return f.name
    return FileStat().name


debug = False


def xmp_func(args):
    if args.xmp_filetypes:
        dump_guessed()
        return
    if args.xmp_file:
        if args.xmp_xml:
            meta = xmp_meta(args.xmp_file)
            meta = str(meta)
            print(meta)
            return

        xmp = xmp_dict(args.xmp_file)
        xmp_c = cleanup_xmp_dict(xmp)

        if args.xmp_tag:
            tags = xmp_tags(xmp_c)
            for k, v in tags:
                print(k, v)
            return

        print(json.dumps(xmp_c, indent=4))


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

    subparsers = parser.add_subparsers(help="sub-command --help")

    xmp_parser = subparsers.add_parser("xmp", help="xmp help")
    xmp_parser.set_defaults(func=xmp_func)

    xmp_parser.add_argument(
        "-types",
        dest="xmp_filetypes",
        action="store_true",
        default=False,
        help="list known xmp file extensions",
    )
    xmp_parser.add_argument(
        "-list",
        type=str,
        dest="xmp_file",
        action="store",
        help="xmp file to inspect",
        default=None,
    )

    xmp_show_opts = xmp_parser.add_mutually_exclusive_group()
    xmp_show_opts.add_argument(
        "-xml",
        dest="xmp_xml",
        action="store_true",
        help="list xmp info as xml",
        default=False,
    )
    xmp_show_opts.add_argument(
        "-tag",
        "-tags",
        dest="xmp_tag",
        action="store_true",
        help="list xmp info as simple tag list",
        default=False,
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug

    if "func" in args:
        debug and print("call func", args.func.__name__)
        rc = args.func(args)
        exit(rc if rc != None else 0)

    if args.show_version:
        print("Version:", VERSION)
        return

    fbase = FileStat(args.base)
    frepo = FileStat(args.dest_repo)
    if fbase.name == frepo.name:
        print("in place processing not supported")
        sys.exit(1)

    return move_pics(fbase.name, frepo, pattern=None, debug=args.debug)


if __name__ == "__main__":
    rc = main_func()
    print(rc)
