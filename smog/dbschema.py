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

from sqlalchemy.orm import declarative_base, relationship


LEN_ID = DBConf.LEN_ID

HASH_LEN = (512 >> 3) << 1

FNAM_LEN = os.pathconf("/", "PC_NAME_MAX")
OS_PATH_LEN = os.pathconf("/", "PC_PATH_MAX")

MEDIA_PATH_LEN = len(build_timed_path_fnam_t(time.time(), ""))
MEDIA_PATH_LEN = MEDIA_PATH_LEN + FNAM_LEN

MEDIA_TYPE_LEN = 1 << 5


Base = declarative_base()


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

    gps = relationship(
        "MediaGPS",
        back_populates="media",
        cascade="all, delete",  # delete-orphan todo?
        uselist=False,  # one to one relationship
    )


class MediaPath(Base):
    __tablename__ = "media_path"

    id = Column(String(LEN_ID), primary_key=True)

    media_id = Column(String(LEN_ID), ForeignKey("media.id"))
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

    lat = Column(Float(), nullable=False)
    lon = Column(Float(), nullable=False)
