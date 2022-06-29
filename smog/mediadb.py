import os
import glob
import json
import time

try:
    from .dbconf import DBConf
    from .dbschema import Base, Setting, Media, MediaPath
    from .file import FileStat, Hash
except:
    from dbconf import DBConf
    from dbschema import Base, Setting, Media, MediaPath
    from file import FileStat, Hash


from sqlalchemy.orm import Session
from sqlalchemy import delete


class MediaDB(object):
    def __init__(self, db_conf, repo_path, base_path):

        self.db_conf = db_conf

        self.repo_path = FileStat(repo_path).name
        self.base_path = FileStat(base_path).name

        self.engine = self.db_conf.open_db()
        self.meta = self.db_conf.create_db_meta(Base)

        self.session = None
        self.begin()

    #

    def add_(self, recs, auto_commit=True):
        self.session.add_all(recs if type(recs) is list else [recs])
        if auto_commit:
            return self.commit()

    def del_(self, recs, auto_commit=True):
        self.session.delete_all(recs if type(recs) is list else [recs])
        if auto_commit:
            return self.commit()

    def begin(self):
        try:
            if self.session:
                self.session.close()
        except Exception as ex:
            print("sqlalchemy", ex)
        self.session = Session(self.engine)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.begin()

    #

    def norm_repo_path(self, fnam):
        if fnam.startswith(self.repo_path):
            return fnam[len(self.repo_path) + 1 :]
        return fnam

    def norm_base_path(self, fnam):
        if fnam.startswith(self.base_path):
            return fnam[len(self.base_path) + 1 :]
        return fnam

    #

    def qry_setting(self, key):
        qry = self.session.query(Setting).where(Setting.key.is_(key))
        sett = qry.one_or_none()
        return sett

    #

    def qry_media_id(self, id):
        qry = self.session.query(Media).where(Media.id.is_(id))
        media = qry.one_or_none()
        return media

    def qry_media_hash(self, hash):
        qry = self.session.query(Media).where(Media.hash.is_(hash))
        recs = qry.all()
        if len(recs) > 1:
            raise Exception("double entry, db corrupted")
        media = recs[0] if len(recs) == 1 else None
        return media

    def qry_media_repo(self, repo_path):
        qry = self.session.query(Media).where(Media.repopath.is_(repo_path))
        recs = qry.all()
        if len(recs) > 1:
            raise Exception("double entry, db corrupted")
        media = recs[0] if len(recs) == 1 else None
        return media

    def qry_media_path(self, base_path):
        qry = self.session.query(MediaPath).where(MediaPath.path.is_(base_path))
        recs = qry.all()
        if len(recs) > 1:
            raise Exception("double entry, db corrupted")
        media = recs[0].media if len(recs) == 1 else None
        return media


#
#
#

if __name__ == "__main__":

    import mimetypes
    from dbconf import SqliteConf
    from organize import build_timed_path_fnam_t

    default_path = "~/Bilder"
    repo_path = "~/media-repo"

    f = FileStat(default_path).join(["20220521.jpeg"])

    fnam, ext = f.splitext()

    hash_ = f.hash()

    dbconf = SqliteConf("media.db", path=".")

    db = MediaDB(dbconf, repo_path, default_path)

    to_insert = False

    media = db.qry_media_hash(hash_)

    if media is None:
        print("add media")
        media = SqliteConf.create_new_with_id(Media)
        media.hash = f.hash()
        media.mime = mimetypes.types_map.get(ext, None)
        # todo
        media.repopath = db.norm_repo_path(f.name)
        to_insert = True

    # todo
    fpath = db.norm_base_path(f.name)

    already_exists = any(filter(lambda x: x.path == fpath, media.paths))

    if not already_exists:
        print("add path")
        mp = SqliteConf.create_new_with_id(MediaPath)
        mp.path = db.norm_base_path(f.name)
        mp.media = media
        to_insert = True

    sett = db.qry_setting("UPDATED")
    if sett is None:
        sett = Setting()
        sett.key = "UPDATED"
        sett.val = 0
    else:
        print(sett.key, sett.val)

    settrun = db.qry_setting("RUN")
    if settrun is None:
        settrun = Setting()
        settrun.key = "RUN"
        settrun.val = 0
    else:
        print(settrun.key, settrun.val)

    settrun.val = int(settrun.val) + 1

    auto_commit = False

    if to_insert:

        sett.val = int(sett.val) + 1

        db.add_([media, mp, sett, settrun], auto_commit=auto_commit)
    else:
        print("nothing to do")
        db.add_(settrun, auto_commit=auto_commit)

    db.commit()
