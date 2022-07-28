import time
from datetime import datetime as DateTime
from dateutil.parser import isoparse
import mimetypes

from .file import FileStat

from .context import Context, CtxPipe, CtxTerm, CtxStop, CtxPrint, CtxProcessor

from .dbconf import DBConf
from .dbschema import (
    Media,
    MediaPath,
    MediaGPS,
    MediaHashtag,
    MediaCollection,
    MediaCollectionItem,
)

from .examine import ifile
from .xmptype import guess_xmp_fnam

from .xmptype import dump_guessed
from .xmpex import xmp_meta
from .xmpex import get_tags, xmp_dict, cleanup_xmp_dict, xmp_tags

from .timeguess import tm_guess_from_fnam
from .gps import get_lat_lon

from .organize import build_timed_path_fnam
from .file1name import make_unique_filename


class Container(object):
    def __init__(self, inp):
        self.inp = inp

    def get(self, nam, default=None):
        return self.__dict__.setdefault(nam, default)

    def merge(self, dic):
        self.__dict__.update(dic)

    def __repr__(self):
        return str(self.__dict__)


#


class CtxPrintFile(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        self.ctx.print(inp.name)
        return c, err


#


class CtxExamine(CtxProcessor):
    def reset(self, ctx):
        super().reset(ctx)

        self.scanlist = self.ctx.scanlist if self.ctx.scanlist else []
        if len(self.scanlist) == 0:
            self.scanlist = [self.ctx.srcdir]

        self.ctx.vprint("to scan", self.scanlist)

        self.iter = self._create_iter()

    def _create_iter(self):
        for fnam in self.scanlist:
            f = FileStat(fnam)

            if not f.exists():
                self.ctx.eprint("not found", f.name)
                continue

            if f.is_file():
                if not f.name.startswith(self.ctx.srcdir + FileStat.sep):
                    self.ctx.eprint("not on source path", f.name)
                    continue
                yield f
                continue

            if not (f.name + FileStat.sep).startswith(self.ctx.srcdir + FileStat.sep):
                self.ctx.eprint("not on source path", f.name)
                continue

            yield from ifile(f.name, recursive=self.ctx.recursive)

    def process(self, inp, err):
        if inp or err:
            raise Exception("must be first in chain")

        # this raises StopIteration
        return Container(next(self.iter)), None


class CtxResetGlobals(CtxProcessor):
    def reset(self, ctx):
        super().reset(ctx)

        # todo ?
        # move to reset of producing ctx flow handlers
        self.ctx.NO_FILES = 0
        self.ctx.NO_COPY_FILES = 0
        self.ctx.NO_COPY_FILES_RENAMED = 0
        self.ctx.NO_COPY_FILES_FAILED = 0
        self.ctx.NO_MOVE_FILES = 0
        self.ctx.NO_MOVE_FILES_FAILED = 0

        self.ctx.NO_DB_CREATED = 0
        self.ctx.NO_DB_UPDATED = 0


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


class CtxMimeType(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        mime, _encoding = mimetypes.guess_type(inp.name)
        c.FILE_MIME = mime
        self.ctx.dprint("mime type", c.FILE_MIME)
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
        c.GPS_LAT_LON = None
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


class CtxFileHash(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        c.FILE_HASH = inp.hash()
        c.FILE_HASH_IDENTICAL = False

        return c, err


class CtxOrganizeRepoPath(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        ts = DateTime(*c.ProcTime_tm[0:6])
        fnam = inp.basename()

        dest_rel = build_timed_path_fnam(ts, fnam)
        c.REPO_DEST_ORG = dest_rel

        dest_repo = FileStat(self.ctx.repodir).join([dest_rel])
        dest_fnam = dest_repo.name

        c.REPO_COPY = True

        if dest_repo.exists():
            if dest_repo.hash() == c.FILE_HASH:
                self.ctx.vprint("identical", inp.name, dest_repo.name)
                c.REPO_COPY = False
                # todo refactor ?
                c.FILE_HASH_IDENTICAL = True
            else:
                if c.DB_REC:
                    # file exists already in db, nothing to do
                    c.REPO_COPY = False
                    c.REPO_DEST_FNAM = c.DB_REC.repopath  # todo check this
                else:
                    dest_fnam = make_unique_filename(dest_repo.name, extname="OBJ")
                    self.ctx.NO_COPY_FILES_RENAMED += 1
                    self.ctx.print("file renamed", inp.name, dest_fnam)

        c.REPO_DEST_FNAM = dest_fnam

        return c, err


class CtxDB_HashLoopup(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        c.DB_REC = None

        rec = self.ctx.db.qry_media_hash(c.FILE_HASH)
        c.DB_REC = rec
        if c.DB_REC:
            pass  # todo logging

        return c, err


class CtxDB_upsert(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        c.DB_REC_DIRTY = False
        c.DB_REC_NEW = False

        if c.REPO_COPY or c.FILE_HASH_IDENTICAL:
            if c.DB_REC:
                rec = c.DB_REC
            else:
                rec = DBConf.create_new_with_id(Media)
                c.DB_REC = rec
                self.ctx.NO_DB_CREATED += 1

                rec.hash = c.FILE_HASH
                rec.repopath = self.ctx.norm_repo_path(c.REPO_DEST_FNAM)
                rec.mime = c.FILE_MIME

                # this might be different from REPO_DEST_FNAM
                rec.filename = inp.basename()

                rec.timestamp = DateTime.fromtimestamp(c.ProcTime)

                c.DB_REC_DIRTY = True
                c.DB_REC_NEW = True

            db_dest_path = self.ctx.norm_src_path(inp.name)
            found = False

            # paths

            c.DB_REC_PATH = None

            for r in rec.paths:
                if r.path == db_dest_path:
                    c.DB_REC_PATH = r
                    found = True
                    break

            if not found or c.DB_REC_NEW:
                prec = DBConf.create_new_with_id(MediaPath)
                prec.path = db_dest_path
                rec.paths.append(prec)
                c.DB_REC_PATH = prec
                c.DB_REC_DIRTY = True

        return c, err


def find_rec_path(rec, path):
    for r in rec.paths:
        if r.path == db_dest_path:
            return r


class CtxDB_gps(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        rec = c.DB_REC

        if rec and c.DB_REC_NEW:
            if c.GPS_LAT_LON:
                if rec.gps is None:
                    gpsrec = DBConf.create_new_with_id(MediaGPS)
                    rec.gps = gpsrec
                    c.DB_REC_DIRTY = True
                else:
                    gpsrec = rec.gps

                if gpsrec.lat != c.GPS_LAT or gpsrec.lon != c.GPS_LON:
                    # todo logging
                    gpsrec.lat = c.GPS_LAT
                    gpsrec.lon = c.GPS_LON
                    c.DB_REC_DIRTY = True

        return c, err


class CtxDB_Hashtag(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        rec = c.DB_REC
        if self.ctx.cleartags:
            self.ctx.dprint("cleartags from record")
            hashtags = rec.hashtags
            self.ctx.db.remove(list(hashtags))
            rec.hashtags.clear()
            c.DB_REC_DIRTY = True

        ht = self.ctx.hashtag
        if ht:
            hashtags = rec.hashtags
            for el in ht:
                found = len(list(filter(lambda x: x.hashtag == el, hashtags))) > 0
                if not found:
                    mhtrec = DBConf.create_new_with_id(MediaHashtag)
                    mhtrec.hashtag = el
                    rec.hashtags.append(mhtrec)
                    c.DB_REC_DIRTY = True
                else:
                    self.ctx.vprint("already tagged")

        return c, err


class CtxDB_Collection(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        rec = c.DB_REC
        if self.ctx.collection:
            self.ctx.vprint("add to collection", self.ctx.collection)

            collection = self.ctx.db.qry_media_collection_name(self.ctx.collection)

            if collection is None:
                self.ctx.dprint("new collection", self.ctx.collection)
                collection = DBConf.create_new_with_id(MediaCollection)
                collection.name = self.ctx.collection

                collection.first_media = rec.timestamp
                collection.last_media = rec.timestamp

                self.ctx.db.upsert(collection)
                c.DB_REC_DIRTY = True

            found = False
            for mediaitem in collection.mediaitems:
                if mediaitem.media_col_item == rec.id:
                    found = True
                    self.ctx.dprint("found media", rec.id)
                    break

            if not found:
                self.ctx.vprint("add media", rec.id)
                mediaitem = DBConf.create_new_with_id(MediaCollectionItem)
                mediaitem.media = rec
                mediaitem.collection_id = collection.id
                self.ctx.db.upsert(mediaitem)
                collection.mediaitems.append(mediaitem)
                #
                collection.first_media = min(collection.first_media, rec.timestamp)
                collection.last_media = max(collection.last_media, rec.timestamp)
                #
                self.ctx.db.upsert(collection)
                c.DB_REC_DIRTY = True
            else:
                self.ctx.vprint("already in collection")

        return c, err


class CtxDB_commit(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.DB_REC_DIRTY:
            self.ctx.dprint("db commit", inp.name, c.DB_REC.id)
            self.ctx.db.upsert(c.DB_REC)
            self.ctx.db.commit()
            c.DB_REC_DIRTY = False
            self.ctx.NO_DB_UPDATED += 1

        return c, err


class CtxCopyToRepoPath(CtxProcessor):
    def process(self, c, err):
        inp = c.inp
        if c.REPO_COPY and self.ctx.move2repo:
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
                self.ctx.eprint("copy to repo", src.name, dest.name, ex)

        return c, err


class CtxMoveToProcPath(CtxProcessor):
    def process(self, c, err):
        inp = c.inp

        relp = c.inp.name[len(self.ctx.srcdir + FileStat.sep) :]
        dest_proc = FileStat(self.ctx.procdir).join([relp]).name

        if self.ctx.move2proc:
            self.vprint("move to proc", inp.name, "->", dest_proc)

            raise Exception("untested")

            try:
                inp.move(dest_proc)
                self.ctx.NO_MOVE_FILES += 1

                r = c.DB_REC_PATH
                r.path = self.ctx.norm_src_path(dest_proc)
                c.DB_REC_DIRTY = True

            except Exception as ex:
                self.ctx.NO_MOVE_FILES_FAILED += 1
                self.ctx.eprint("move to proc", src.name, dest.name, ex)

            # todo
            # currently move is not supported
            raise StopIteration()
        else:
            self.ctx.dprint("no move to proc", inp.name, dest_proc)

        return c, err


def build_scan_flow(pipe):
    # keep this first
    pipe.add(CtxExamine())

    # keep this second
    pipe.add(CtxResetGlobals())
    #
    pipe.add(CtxExcludeFolder())
    pipe.add(CtxProcFile())
    pipe.add(CtxMimeType())
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
    pipe.add(
        CtxTime_proc(
            [
                "XMPtime",
                "EXIFtime",
                "FNAMtime",
                "FILEtime",
            ]
        )
    )

    pipe.add(CtxListFileNameTimeMeth())
    pipe.add(CtxListFileTimeMeth())

    pipe.add(CtxFileHash())
    pipe.add(CtxDB_HashLoopup())

    pipe.add(CtxOrganizeRepoPath())

    pipe.add(CtxDB_upsert())
    pipe.add(CtxDB_gps())
    pipe.add(CtxDB_Hashtag())
    pipe.add(CtxDB_Collection())

    pipe.add(CtxDB_commit())

    pipe.add(CtxCopyToRepoPath())

    pipe.add(CtxMoveToProcPath())
    # after move to proc path an update might be required
    pipe.add(CtxDB_commit())

    #
    # pipe.add(CtxStop())
    # add other processors here
    #
    None
    # keep this last, otherwise it run's forever
    pipe.add(CtxTerm())
