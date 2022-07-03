try:
    from .dbconf import DBConf
    from .dbschema import Base, Setting, Media, MediaPath
except:
    from dbconf import DBConf
    from dbschema import Base, Setting, Media, MediaPath

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc


class MediaDB(object):
    def __init__(self, db_conf):

        self.db_conf = db_conf

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

    #

    def upsert(self, recs, auto_commit=False):
        return self.add_(recs=recs, auto_commit=auto_commit)

    def remove(self, recs, auto_commit=False):
        return self.remove(recs=recs, auto_commit=auto_commit)

    #

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

    def qry_media_time(self, timestamp=None):

        raise Exception("draft, untested")

        if timestamp is None:
            timestamp = dt.now()

        qry = self.session.query(Media).where(Media.timestamp <= timestamp)

        qry = qry.order_by(desc(Media.timestamp))
        return qry
