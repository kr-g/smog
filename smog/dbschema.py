import os
import time

try:
    from .dbconf import DBConf
    from .organize import build_timed_path_fnam_t
except:
    from dbconf import DBConf
    from organize import build_timed_path_fnam_t


from sqlalchemy import Column, ForeignKey

from sqlalchemy import String

# from sqlalchemy import Boolean
# from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime

from sqlalchemy.orm import declarative_base, relationship


LEN_ID = DBConf.LEN_ID

HASH_LEN = (512 >> 3) << 1

FNAM_LEN = os.pathconf("/", "PC_NAME_MAX")
OS_PATH_LEN = os.pathconf("/", "PC_PATH_MAX")

MEDIA_PATH_LEN = len(build_timed_path_fnam_t(time.time(), ""))
MEDIA_PATH_LEN = MEDIA_PATH_LEN + FNAM_LEN

MEDIA_TYPE_LEN = 1 << 5

LEN_HASHTAG = 128
LEN_COLLECTION = 256

Base = declarative_base()


class Setting(Base):
    __tablename__ = "setting"
    key = Column(String(32), primary_key=True)
    val = Column(String(256), nullable=True)


class Media(Base):
    __tablename__ = "media"

    id = Column(String(LEN_ID), primary_key=True)

    hash = Column(String(HASH_LEN), index=True, nullable=False)  # , unique=True todo ?

    repopath = Column(String(MEDIA_PATH_LEN), index=True, nullable=False)

    mime = Column(String(MEDIA_TYPE_LEN), nullable=True)

    filename = Column(String(FNAM_LEN), index=True, nullable=False)

    timestamp = Column(DateTime(), index=True, nullable=False)

    paths = relationship(
        "MediaPath",
        back_populates="media",
        cascade="all, delete",
    )

    gps = relationship(
        "MediaGPS",
        back_populates="media",
        cascade="all, delete",  # delete-orphan todo?
        uselist=False,  # one to one relationship
    )

    hashtags = relationship(
        "MediaHashtag",
        back_populates="media",
        cascade="all, delete",
    )

    media_collection_items = relationship(
        "MediaCollectionItem",
        back_populates="media",
        cascade="all, delete",
        overlaps="media, media_col_item",
    )


class MediaPath(Base):
    __tablename__ = "media_path"

    id = Column(String(LEN_ID), primary_key=True)

    media_id = Column(
        String(LEN_ID), ForeignKey("media.id"), index=True, nullable=False
    )
    media = relationship(
        "Media",
        back_populates="paths",
    )

    path = Column(String(OS_PATH_LEN), index=True, nullable=False)


class MediaGPS(Base):
    __tablename__ = "media_gps"

    media_id = Column(String(LEN_ID), ForeignKey("media.id"), primary_key=True)
    media = relationship(
        "Media",
        back_populates="gps",
    )

    lat = Column(Float(), index=True, nullable=False)
    lon = Column(Float(), index=True, nullable=False)


class MediaHashtag(Base):
    __tablename__ = "media_hashtag"

    id = Column(String(LEN_ID), primary_key=True)

    media_id = Column(
        String(LEN_ID), ForeignKey("media.id"), index=True, nullable=False
    )
    media = relationship(
        "Media",
        back_populates="hashtags",
    )

    hashtag = Column(String(LEN_HASHTAG), index=True, nullable=False)


class MediaCollection(Base):
    __tablename__ = "media_collection"

    id = Column(String(LEN_ID), primary_key=True)

    name = Column(String(LEN_COLLECTION), index=True, nullable=False)

    first_media = Column(DateTime(), index=True, nullable=False)
    last_media = Column(DateTime(), index=True, nullable=False)

    mediaitems = relationship(
        "MediaCollectionItem",
        back_populates="media_collection",
        cascade="all, delete",
    )


class MediaCollectionItem(Base):
    __tablename__ = "media_col_item"

    id = Column(String(LEN_ID), primary_key=True)

    media_collection_id = Column(
        String(LEN_ID), ForeignKey("media_collection.id"), index=True, nullable=False
    )
    media_collection = relationship(
        "MediaCollection",
        back_populates="mediaitems",
    )

    media_col_item = Column(
        String(LEN_ID), ForeignKey("media.id"), index=True, nullable=False
    )
    media = relationship(
        "Media",
        backref="media_col_item",
    )
