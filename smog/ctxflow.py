import time

from .file import FileStat

from .context import Context, CtxPipe, CtxTerm, CtxStop, CtxPrint, CtxProcessor
from .dbconf import SqliteConf
from .dbmedia import MediaDB

from .examine import ifile
from .xmptype import guess_xmp_fnam

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import get_tags, xmp_dict, cleanup_xmp_dict, xmp_tags

from .timeguess import tm_guess_from_fnam
from .gps import get_lat_lon

from .organize import build_timed_path_fnam
from .file1name import make_unique_filename

from datetime import datetime as dt
from dateutil.parser import isoparse


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

        self.ctx.NO_FILES = 0
        self.ctx.NO_COPY_FILES = 0
        self.ctx.NO_COPY_FILES_FAILED = 0

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


class CtxProcFile(CtxProcessor):
    def process(self, c, err):
        self.ctx.NO_FILES += 1
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
            gps = {}
            for k, v in tags:
                if k.startswith("exif:GPS"):
                    key = k[len("exif:") :]
                    self.ctx.vprint(key, v)
                    gps[key] = v
            if len(gps.keys()) > 0:
                c.get("EXIF_GPS", gps)
                self.ctx.dprint("gps info", c.EXIF_GPS)
        return c, err


class CtxEXIF_GPSconv(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        gpsinfo = c.get("EXIF_GPS")
        if gpsinfo:
            try:
                lat, lon = get_lat_lon(gpsinfo)
                c.GPS_LAT = lat
                c.GPS_LON = lon
                c.GPS_LAT_LON = lat, lon
            except Exception as ex:
                c.GPSerror = True
                self.ctx.eprint("gps conv", inp.name, gpsinfo, ex)
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
    def __init__(self, props):
        super().__init__()
        self.props = props

    def process(self, c, err):
        inp = c.inp
        for prop in self.props:
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


class CtxOrganizeRepoPath(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        ts = dt(*c.ProcTime_tm[0:6])
        fnam = inp.basename()

        dest_rel = build_timed_path_fnam(ts, fnam)
        c.REPO_DEST_ORG = dest_rel

        dest_repo = FileStat(self.ctx.repodir).join([dest_rel])
        dest_fnam = dest_repo.name

        c.REPO_COPY = True

        c.FILE_HASH = inp.hash()

        if dest_repo.exists():
            if dest_repo.hash() == c.FILE_HASH:
                self.ctx.vprint("identical", inp.name, dest_repo.name)
                c.REPO_COPY = False
            else:
                dest_fnam = make_unique_filename(dest_repo.name)

        c.REPO_DEST_FNAM = dest_fnam

        return c, err


class CtxCopyToRepoPath(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.REPO_COPY:
            src = inp
            dest = FileStat(c.REPO_DEST_FNAM)
            c.REPO_COPY_OK = False
            try:
                rc = src.move(dest.name, mkcopy=True, dryrun=False)
                self.ctx.dprint("copy to repo, move", rc)
                tm = c.ProcTime
                dest.touch_ux((tm, tm))
                c.REPO_COPY_OK = True

                self.ctx.NO_COPY_FILES += 1
                self.ctx.vprint("copy to repo", src.name, "->", dest.name, "@", tm)

            except Exception as ex:
                self.ctx.NO_COPY_FILES_FAILED += 1
                self.ctx.eprint("copy to repo", src.name, dest.name, tm, ex)

        return c, err


def build_scan_flow(pipe):
    # keep this first
    pipe.add(CtxExamine())
    #
    pipe.add(CtxExcludeFolder())
    pipe.add(CtxProcFile())
    #
    pipe.add(CtxFile_datetime())
    pipe.add(CtxFileName_datetime())

    pipe.add(CtxCheckXMP())
    pipe.add(CtxXMP_tags())
    pipe.add(CtxXMP_datetime())

    # after xmp processing
    pipe.add(CtxEXIF_datetime())
    pipe.add(CtxEXIF_GPS())
    pipe.add(CtxEXIF_GPSconv())

    # after all timestamps have processed
    pipe.add(CtxTime_proc(["XMPtime", "EXIFtime", "FNAMtime", "FILEtime"]))

    pipe.add(CtxListFileNameTimeMeth())
    pipe.add(CtxListFileTimeMeth())

    pipe.add(CtxOrganizeRepoPath())
    pipe.add(CtxCopyToRepoPath())
    #
    # pipe.add(CtxStop())
    # add other processors here
    #
    None
    # keep this last, otherwise it might run forever
    pipe.add(CtxTerm())
