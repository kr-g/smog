import sys

import json
import argparse

from .file import FileStat
from .movepic import move_pics

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import xmp_dict, cleanup_xmp_dict, xmp_tags

from .context import Context, CtxPipe, CtxTerm
from .dbconf import SqliteConf
from .mediadb import MediaDB

from .examine import CtxExamine

#

VERSION = "v0.0.2-a"


#

args = None
debug = False
verbose = False


def dprint(*args, **kwargs):
    global debug
    debug and print("DEBUG", *args, **kwargs)


def vprint(*args, **kwargs):
    global verbose
    verbose and print(*args, **kwargs)


def wprint(*args, **kwargs):
    print("WARNING", *args, **kwargs)


def eprint(*args, **kwargs):
    print("ERROR", *args, **kwargs)


def print_err(*args, **kwargs):
    eprint(*args, **kwargs)


#


def get_default_pic_folder():
    flds = ["~/Bilder", "~/Pictures"]
    for d in flds:
        f = FileStat(d, prefetch=True)
        if f.is_dir():
            return f.name
    return FileStat().name


def is_folder_or_die(f):
    if f.exists() and not f.is_dir():
        eprint("not a folder", f.name)
        sys.exit(1)


#


def scan_func(args):

    pipe = CtxPipe(args.ctx)
    # keep this first
    pipe.add(CtxExamine())
    #

    # add other processors here
    #
    None
    # keep this last, otherwise it might run forever
    pipe.add(CtxTerm())

    pipe.reset()

    noitems = 0

    while True:
        try:
            pipe.process()
            noitems += 1
        except StopIteration:
            args.ctx.vprint("done", noitems)
            break


#


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

    global debug, verbose

    parser = argparse.ArgumentParser(
        prog="smog",
        usage="python3 -m %(prog)s [options]",
        description="simple media organizer",
        epilog="for more information refer to https://github.com/kr-g/smog",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "--verbose",
        "-V",
        dest="verbose",
        action="store_true",
        help="show more info (default: %(default)s)",
        default=verbose,
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
        metavar="SRC_DIR",
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

    proc_dir = FileStat(base).join(["proc-media"])

    parser.add_argument(
        "-proc",
        type=str,
        dest="proc_dir",
        action="store",
        metavar="PROC_DIR",
        help="processed file folder. subfolder of SRC_DIR. (default: %(default)s)",
        default=proc_dir.name,
    )

    parser.add_argument(
        "-exclude-folder",
        "-no-scan",
        type=str,
        dest="exclude_dirs",
        action="store",
        nargs="+",
        metavar="EXCLUDE_DIR",
        help="exclude folder from scan",
        default=None,
    )

    subparsers = parser.add_subparsers(help="sub-command --help")

    # scan

    scan_parser = subparsers.add_parser("scan", help="scan --help")
    scan_parser.set_defaults(func=scan_func)

    # xmp

    xmp_parser = subparsers.add_parser("xmp", help="xmp --help")
    xmp_parser.set_defaults(func=xmp_func)

    xmptypes = xmp_parser.add_argument_group("known files")
    xmptypes.add_argument(
        "-types",
        dest="xmp_filetypes",
        action="store_true",
        default=False,
        help="list known xmp file extensions",
    )

    xmpmeta = xmp_parser.add_argument_group("xmp meta")
    xmpmeta.add_argument(
        "-list",
        type=str,
        dest="xmp_file",
        action="store",
        help="xmp file to inspect",
        default=None,
    )

    xmp_show_opts = xmpmeta.add_mutually_exclusive_group()
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

    debug = args.debug
    dprint("arguments", args)

    verbose = args.verbose

    args.base = FileStat(args.base)
    is_folder_or_die(args.base)

    args.dest_repo = FileStat(args.dest_repo)
    is_folder_or_die(args.dest_repo)

    if args.base.name == args.dest_repo.name:
        print_err("in place processing not supported")
        sys.exit(1)

    args.proc_dir = FileStat(args.proc_dir)
    is_folder_or_die(args.proc_dir)

    if args.exclude_dirs:
        args.exclude_dirs = list(
            map(lambda x: FileStat(x, prefetech=True), args.exclude_dirs)
        )

        for nam in args.exclude_dirs:
            f = FileStat(nam, prefetch=True)
            is_folder_or_die(f)
        args.exclude_dirs = list(map(lambda x: x.name, args.exclude_dirs))

    dbconf = SqliteConf("smog.db", path="..")
    db = MediaDB(dbconf)

    args.ctx = Context(
        args.base.name,
        args.dest_repo.name,
        args.proc_dir.name,
        db=db,
        excludedirs=args.exclude_dirs,
        verbose=verbose,
        debug=debug,
    )

    if "func" in args:
        dprint("call func", args.func.__name__)
        rc = args.func(args)
        return rc if rc != None else 0

    rc = move_pics(fbase.name, frepo, pattern=None, debug=args.debug)
    dprint("files total/ processed", rc)


if __name__ == "__main__":
    rc = main_func()
    print(rc)
