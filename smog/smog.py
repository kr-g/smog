import sys
import time
import json
import argparse

from .file import FileStat
from .movepic import move_pics

from .context import Context, CtxPipe, CtxTerm, CtxStop, CtxPrint, CtxProcessor
from .dbconf import SqliteConf
from .mediadb import MediaDB

from .examine import ifile
from .xmptype import guess_xmp_fnam

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import get_tags, xmp_dict, cleanup_xmp_dict, xmp_tags

from .timeguess import tm_guess_from_fnam

from dateutil.parser import isoparse


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


class Container(object):
    def __init__(self, inp):
        self.inp = inp

    def get(self, nam, default=None):
        return self.__dict__.setdefault(nam, default)

    def merge(self, dic):
        self.__dict__.update(dic)

    def __repr__(self):
        return str(self.__dict__)


class CtxExamine(CtxProcessor):
    def reset(self, ctx):
        super().reset(ctx)
        self.iter = ifile(self.ctx.srcdir, recursive=self.ctx.recursive)

    def process(self, inp, err):
        if inp or err:
            raise Exception("must be first in chain")

        # this raises StopIteration
        return Container(next(self.iter)), None


class CtxExcludeFolder(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        for f in self.ctx.excludedirs:
            if inp.name.startswith(f + FileStat.sep):
                self.ctx.dprint("filtered", inp)
                return None, None
        return c, err


class CtxCheckXMP(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        c.XMPscan = guess_xmp_fnam(inp.name)
        self.ctx.vprint("xmp scan", c.XMPscan, inp.name)
        return c, err


class CtxXMP_tags(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.get("XMPscan"):
            try:
                c.XMP = xmp_meta(inp.name)
                self.ctx.vprint("xmp scan ok")
                self.ctx.dprint(c.XMP)

                c.XMPtags = get_tags(inp.name)
                c.XMPdict = dict(c.XMPtags)
                [self.ctx.dprint(x) for x in c.XMPtags]

            except Exception as ex:
                self.ctx.wprint("xmp load failed", inp.name)

        return c, err


def parse_iso_tm(isodate):
    return isoparse(isodate).timetuple()


def conv_tm(tm):
    return time.mktime(tm)


class CtxXMP_datetime(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.get("XMPdict"):
            try:
                c.XMPtime_raw = c.XMPdict.get("xmp:CreateDate")
                if c.XMPtime_raw:
                    c.XMPtime_tm = parse_iso_tm(c.XMPtime_raw)
                    self.ctx.vprint("xmp isodate", c.XMPtime_tm)
                    c.XMPtime = conv_tm(c.XMPtime_tm)
            except Exception as ex:
                self.ctx.eprint("xmp timeformat", inp.name, ex)
        return c, err


class CtxEXIF_datetime(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.get("XMPdict"):
            try:
                c.EXIFtime_raw = c.XMPdict.get("exif:DateTimeOriginal")
                if c.EXIFtime_raw:
                    c.EXIFtime_tm = parse_iso_tm(c.EXIFtime_raw)
                    self.ctx.vprint("exif isodate", c.EXIFtime_tm)
                    c.EXIFtime = conv_tm(c.EXIFtime_tm)
            except Exception as ex:
                self.ctx.eprint("exif timeformat", inp.name, ex)
        return c, err


class CtxEXIF_GPS(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        tags = c.get("XMPtags")
        if tags:
            for k, v in tags:
                if k.startswith("exif:GPS"):
                    key = k[len("exif:") :]
                    c.get(key, v)
                    self.ctx.vprint(key, v)
        return c, err


class CtxFileName_datetime(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        try:
            c.FNAMtime_tm = tm_guess_from_fnam(inp.name)
            c.FNAMtime = conv_tm(c.FNAMtime_tm)
            self.ctx.dprint("file name time", c.FNAMtime)
            self.ctx.vprint("file name time_tm", c.FNAMtime_tm)
        except:
            pass
        return c, err


class CtxFile_datetime(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        # first time or mtime ???
        # todo ?
        c.FILEtime_tm = inp.ftime()
        c.FILEtime = conv_tm(c.FILEtime_tm)
        self.ctx.dprint("file time", c.FILEtime)
        self.ctx.vprint("file time_tm", c.FILEtime_tm)
        return c, err


class CtxTime_proc(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        for prop in ["XMPtime", "EXIFtime", "FNAMtime", "FILEtime"]:
            p = c.get(prop)
            if p:
                c.ProcTime = c.get(prop)
                c.ProcTime_tm = c.get(prop + "_tm")
                c.ProcTimeMeth = prop
                break
        self.ctx.dprint("proc time meth", c.ProcTimeMeth)
        self.ctx.dprint("proc time", c.ProcTime)
        self.ctx.vprint("proc time_tm", c.ProcTime_tm)
        return c, err


class CtxListFileNameTimeMeth(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        meth = c.get("ProcTimeMeth")
        if meth == "FNAMtime":
            self.ctx.print("FNAMtime", inp.name)
            for k, v in c.__dict__.items():
                if k.lower().find("time") >= 0:
                    self.ctx.dprint(k, v)
        return c, err


class CtxListFileTimeMeth(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        meth = c.get("ProcTimeMeth")
        if meth == "FILEtime":
            self.ctx.print("FILEtime", inp.name)
            for k, v in c.__dict__.items():
                if k.lower().find("time") >= 0:
                    self.ctx.dprint(k, v)
        return c, err


def scan_func(args):

    pipe = CtxPipe(args.ctx)
    # keep this first
    pipe.add(CtxExamine())
    #
    pipe.add(CtxExcludeFolder())

    pipe.add(CtxFile_datetime())
    pipe.add(CtxFileName_datetime())

    pipe.add(CtxCheckXMP())
    pipe.add(CtxXMP_tags())
    pipe.add(CtxXMP_datetime())

    pipe.add(CtxEXIF_datetime())
    pipe.add(CtxEXIF_GPS())

    pipe.add(CtxTime_proc())

    pipe.add(CtxListFileNameTimeMeth())
    pipe.add(CtxListFileTimeMeth())

    #
    # pipe.add(CtxStop())
    # add other processors here
    #
    None
    # keep this last, otherwise it might run forever
    pipe.add(CtxTerm())
    #
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

    print("what? use --help")


if __name__ == "__main__":
    rc = main_func()
    print(rc)
