import os
import glob
import json
import uuid
import time

try:
    from .file import FileStat, Hash
    from .organize import build_timed_path_fnam_t
except:
    from file import FileStat, Hash
    from organize import build_timed_path_fnam_t

import mimetypes

from sqlalchemy import Column, ForeignKey

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import delete


def create_id():
    return uuid.uuid4().hex


_a_id = create_id()
LEN_ID = len(_a_id)

Base = declarative_base()

HASH_LEN = (512 >> 3) << 1

FNAM_LEN = os.pathconf("/", "PC_NAME_MAX")
OS_PATH_LEN = os.pathconf("/", "PC_PATH_MAX")

MEDIA_PATH_LEN = len(build_timed_path_fnam_t(time.time(), ""))
MEDIA_PATH_LEN = MEDIA_PATH_LEN + FNAM_LEN

MEDIA_TYPE_LEN = 1 << 5

DB_DEFAULT_PATH = "~"


class Setting(Base):
    __tablename__ = "setting"
    key = Column(String(32), primary_key=True)
    val = Column(String(256), nullable=True)


class Media(Base):
    __tablename__ = "media"

    id = Column(String(LEN_ID), primary_key=True)

    hash = Column(String(HASH_LEN), index=True, nullable=False)
    repopath = Column(String(MEDIA_PATH_LEN), index=True, nullable=False)
    mime = Column(String(MEDIA_TYPE_LEN), nullable=True)

    paths = relationship(
        "MediaPath",
        back_populates="media",
        cascade="all, delete",
    )


class MediaPath(Base):
    __tablename__ = "media_path"

    id = Column(String(LEN_ID), primary_key=True)

    path = Column(String(OS_PATH_LEN), index=True, nullable=False)

    media_id = Column(String(LEN_ID), ForeignKey("media.id"))
    media = relationship(
        "Media",
        back_populates="paths",
    )


def create_new_with_id(cls_):
    obj = cls_()
    obj.id = create_id()
    return obj


def get_db_path(path=None):
    if path is None:
        path = DB_DEFAULT_PATH
    db_path = FileStat(path).join(["media.db"])
    return db_path.name


def get_db_spec(db_path):
    db_path = "sqlite://" + os.sep + db_path
    print("db_path", db_path)
    return db_path


def open_db(db_spec, echo=False):
    engine = create_engine(db_spec, echo=echo)
    return engine


def create_db_meta(engine):
    meta = Base.metadata.create_all(engine)
    return meta


class MediaDB(object):
    def __init__(self, db_path, repo_path, base_path):
        self.db_path = FileStat(db_path).name

        self.repo_path = FileStat(repo_path).name
        self.base_path = FileStat(base_path).name

        self.db_file = get_db_path(db_path)
        self.db_spec = get_db_spec(self.db_file)

        self.engine = open_db(self.db_spec)
        self.meta = create_db_meta(self.engine)

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

    # todo, remove

    def add_media(self, media, auto_commit=True):
        return self.add_(media, auto_commit=auto_commit)

    def del_media(self, media, auto_commit=True):
        return self.del_(media, auto_commit=auto_commit)

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
    default_path = "~/Bilder"
    repo_path = "~/media-repo"

    f = FileStat(default_path).join(["20220521.jpeg"])

    fnam, ext = f.splitext()

    hash_ = f.hash()

    db = MediaDB(".", repo_path, default_path)

    to_insert = False

    media = db.qry_media_hash(hash_)

    if media is None:
        print("add media")
        media = create_new_with_id(Media)
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
        mp = create_new_with_id(MediaPath)
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
