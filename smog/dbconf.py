import os
import uuid

from sqlalchemy import create_engine

try:
    from .file import FileStat
except:
    from file import FileStat


class DBConf(object):
    def __init__(self):
        pass

    # static
    def create_id():
        return uuid.uuid4().hex

    LEN_ID = len(create_id())

    def create_new_with_id(cls_):
        obj = cls_()
        obj.id = DBConf.create_id()
        return obj

    #

    def get_schema(self):
        raise NotImplementedError("abstract base class. use sub-class.")

    def set_db_path(dbnam, path=None):
        raise NotImplementedError("abstract base class. use sub-class.")

    #

    def get_credit(self):
        pass

    def get_auth(self):
        credit = self.get_credit()
        if credit:
            return credit + "@"
        return ""

    def get_db_path(self):
        return self.db_path

    def set_db_spec(self):
        self.db_spec = self.get_schema() + self.get_auth() + self.get_db_path()
        return self.db_spec

    def open_db(self, echo=False):
        self.set_db_spec()
        self.engine = create_engine(self.db_spec, echo=echo)
        return self.engine

    def create_db_meta(self, base):
        self.meta = base.metadata.create_all(self.engine)
        return self.meta

    def close_db(self, force_all=False):
        rc = self.engine.dispose(close=force_all)
        self.engine = None
        return rc


class SqliteConf(DBConf):

    DB_DEFAULT_PATH = "~"

    def __init__(self, dbnam=None, path=None):
        super().__init__()
        if dbnam:
            self.set_db_path(dbnam, path)

    def get_schema(self):
        return "sqlite://"

    def set_db_path(self, dbnam, path=None):
        if path is None:
            path = SqliteConf.DB_DEFAULT_PATH
        self.db_path = os.sep + FileStat(path).join([dbnam]).name
        return self.db_path
