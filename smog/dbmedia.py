try:
    from .dbschema import (
        Base,
        Setting,
        Media,
        MediaPath,
        MediaCollection,
        MediaCollectionItem,
        MediaHashtag,
    )
except:
    from dbschema import (
        Base,
        Setting,
        Media,
        MediaPath,
        MediaCollection,
        MediaCollectionItem,
        MediaHashtag,
    )

from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct, asc, desc


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
        if type(recs) is not list:
            recs = [recs]
        for rec in recs:
            self.session.delete(rec)
        if auto_commit:
            return self.commit()

    #

    def upsert(self, recs, auto_commit=False):
        return self.add_(recs=recs, auto_commit=auto_commit)

    def remove(self, recs, auto_commit=False):
        return self.del_(recs=recs, auto_commit=auto_commit)

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

    def qry_media_stream(
        self,
        timestamp=None,
        skip_offset=None,
        hashtag=None,
        collection=None,
        collectionid=None,
        last_as_first_order=True,
    ):

        qry = self.session.query(Media)

        if timestamp:
            qry = qry.where(Media.timestamp <= timestamp)

        if last_as_first_order:
            qry = qry.order_by(desc(Media.timestamp))
        else:
            qry = qry.order_by(asc(Media.timestamp))

        if hashtag:
            if type(hashtag) is not list:
                hashtag = [hashtag]
            hashtag = list(map(lambda x: "#" + x.lower(), hashtag))
            if len(hashtag) > 0:
                qry = qry.join(MediaHashtag).filter(MediaHashtag.hashtag.in_(hashtag))

        if collection and collectionid:
            print("confused by collection name and id being set")

        if collection:
            _name = collection.strip().lower()
            if len(_name) > 0:
                qry = qry.join(MediaCollectionItem).filter(
                    MediaCollectionItem.media_col_item == Media.id
                )
                qry = qry.join(MediaCollection).filter(
                    # todo refactor
                    func.lower(MediaCollection.name)
                    == _name
                )
        elif collectionid:
            _id = collectionid.strip().lower()
            if len(_id) > 0:
                qry = qry.join(MediaCollectionItem).filter(
                    MediaCollectionItem.media_col_item == Media.id
                )
                qry = qry.join(MediaCollection).filter(
                    # todo refactor
                    func.lower(MediaCollection.id)
                    == _id
                )

        if skip_offset:
            qry = qry.offset(skip_offset)

        qry = qry.execution_options(
            stream_results=True,
            yield_per=50,
        )

        def _it():
            for raw in self.session.execute(qry):
                yield raw._data[0]

        return _it()

    #

    def qry_media_collection(self, collectionid):
        qry = self.session.query(MediaCollection)
        qry = qry.where(MediaCollection.id.is_(collectionid))
        collection = qry.one_or_none()
        return collection

    def qry_media_collection_name_stream(
        self, name=None, timestamp=None, skip_offset=None
    ):

        qry = self.session.query(MediaCollection)

        if timestamp:
            qry = qry.where(MediaCollection.last_media <= timestamp)

        if name:
            _name = name.strip().lower()
            if len(_name) > 0:
                qry = qry.where(func.lower(MediaCollection.name) == _name)

        qry = qry.order_by(desc(MediaCollection.last_media))

        if skip_offset:
            qry = qry.offset(skip_offset)

        qry = qry.execution_options(
            stream_results=True,
            yield_per=50,
        )

        def _it():
            for raw in self.session.execute(qry):
                yield raw._data[0]

        return _it()

    def qry_media_collection_name(self, name=None):
        """return first match"""
        for rec in self.qry_media_collection_name_stream(name=name):
            return rec

    #

    def norm_hashtag(self, hashtag):
        if hashtag:
            hashtag = hashtag.strip().lower()
            if len(hashtag) == 0:
                hashtag = None
        return hashtag

    def qry_hashtag_drop(self, hashtag):
        hashtag = self.norm_hashtag(hashtag)
        if hashtag is None:
            return
        qry = self.session.query(MediaHashtag)
        qry = qry.where(MediaHashtag.hashtag == hashtag)
        return qry.delete()

    def qry_hashtag(self, hashtag=None):
        hashtag = self.norm_hashtag(hashtag)
        if hashtag is None:
            qry = self.session.query(distinct(MediaHashtag.hashtag))
        else:
            qry = self.session.query(MediaHashtag)
            qry = qry.where(MediaHashtag.hashtag == hashtag)

        qry = qry.execution_options(
            stream_results=True,
            yield_per=50,
        )

        def _it():
            for raw in self.session.execute(qry):
                yield raw._data[0]

        return _it()

    def qry_hashtag_name(self, name=None):
        """return first match"""
        for rec in self.qry_hashtag(name=name):
            return rec
