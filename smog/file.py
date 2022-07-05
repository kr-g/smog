"""
    (c)2022 K. Goger - https://github.com/kr-g
    legal: https://github.com/kr-g/smog/blob/main/LICENSE.md
"""


import sys
import os
import shutil

import stat
import time

import tempfile

from collections import namedtuple, ChainMap
import glob

import hashlib

DEFAULT_BLOCK_SIZE = 2**16


class PushDir(object):
    @staticmethod
    def basedir(path=None, create=False):
        def _func(func):
            def decor(*args, **kwargs):
                with PushDir(path, create):
                    return func(*args, **kwargs)

            return decor

        return _func

    def __init__(self, path=None, create=False):
        self._path = path
        self._create = create
        self._cwd = os.path.abspath(os.getcwd())

    def __enter__(self):
        if self._path:
            self._path = os.path.expandvars(self._path)
            self._path = os.path.expanduser(self._path)
            self._path = os.path.abspath(self._path)
            if self._create:
                os.makedirs(self._path, exist_ok=True)

            os.chdir(self._path)
        return self

    def __exit__(self, extype, exval, traceb):
        os.chdir(self._cwd)
        return self

    def __repr__(self):
        return self.__class__.__name__ + '( "' + self._cwd + '" )'


class FileStat(object):

    sep = os.sep

    Time = namedtuple("Time", ["ctime", "atime", "mtime"])

    def __init__(self, name=".", expand=True, prefetch=False):
        self.name = name
        self._stat = None
        if expand == True and name != None:
            self.expandall()
        if prefetch:
            self.stat()

    def clone(self):
        return FileStat(self.name)

    def __repr__(self):
        return (
            self.__class__.__name__
            + "('"
            + str(self.name)
            + "', "
            + str(self._stat)
            + ")"
        )

    def stat(self):
        """most class methods expect stat() called first. NoneType exception when not loaded"""
        try:
            self._stat = os.stat(self.name)
            return self._stat
        except Exception as ex:
            pass
            # print(ex, self.name)

    def read_stat(self):
        self.stat()
        return self

    def clr_stat(self):
        self._stat = None
        return self

    # base

    def exists(self):
        return self.stat() != None

    def mode(self):
        return self._stat.st_mode

    def is_file(self):
        return stat.S_ISREG(self.mode())

    def is_link(self):
        return os.path.islink(self.name)

    def is_dir(self):
        return stat.S_ISDIR(self.mode())

    #

    def __len__(self):
        return self.size()

    def size(self):
        l = self.stat()
        if l == None:
            return
        return self._stat.st_size

    # path file ext

    def dirname(self):
        return os.path.dirname(self.name)

    def basename(self):
        return os.path.basename(self.name)

    def splitext(self):
        return os.path.splitext(self.basename())

    # split into dirname basename ext

    def split(self):
        return self.dirname(), *self.splitext()

    # removes common path

    def stripbase(self, base, clobber=True, with_dot=True):
        base = self.expandpath(base) + os.sep
        name = self.name
        if name.startswith(base):
            name = name[len(base) :]
            if with_dot:
                name = "." + os.sep + name
            if clobber:
                self.name = name
        return name

    # path

    def makedirs(self, is_file=True, mode=0o777):
        """set is_file to False to create folder"""
        path = self.name
        if is_file == True:
            path = os.path.dirname(path)
        os.makedirs(path, mode=mode, exist_ok=True)
        return path

    def join(self, path, expand_clobber=True, append=True):
        if append:
            self.name = FileStat.joinpath([self.name, *path], expand_clobber)
        else:
            self.name = FileStat.joinpath(path, expand_clobber)
        return self

    # os and user var

    def expandall(self, clobber=True):
        fpath = self.expandpath(self.name)
        if clobber:
            self.name = fpath
        return fpath

    @staticmethod
    def expandpath(fpath):
        fpath = os.path.expandvars(fpath)
        fpath = os.path.expanduser(fpath)
        fpath = os.path.abspath(fpath)
        return fpath

    @staticmethod
    def joinpath(path, expand=True):
        path = os.path.join(*path)
        if expand:
            path = FileStat.expandpath(path)
        return path

    # temp helpers

    @staticmethod
    def get_tempdir():
        return tempfile.gettempdir()

    # def get_tempfile(suffix=None, prefix=None,):
    #    """this file is not deleted automatically"""
    #    return tempfile.mkstemp(suffix=suffix, prefix=prefix,)

    # os env helpers

    _env = {}
    _overlay = ChainMap(_env, os.environ)

    @staticmethod
    def clrenv():
        """
        clear overlay env settings
        """
        FileStat._env.clear()

    @staticmethod
    def setenv(k, v, overlay=False):
        if overlay:
            if v is not None:
                FileStat._env[k] = v
            else:
                del FileStat._env[k]
        else:
            os.environ[k] = v

    @staticmethod
    def getenv(k):
        return FileStat._overlay[k]

    # first and last access time
    # looking on _all_ time stamps

    def ftime(self, conv_tm=True):
        """first access time, base utc like time.time()"""
        return self._cmptime(
            cmp=min, cmpval=sys.maxsize, conv=time.gmtime if conv_tm else None
        )

    def ltime(self, conv_tm=True):
        """last access time, base utc like time.time()"""
        return self._cmptime(cmp=max, cmpval=0, conv=time.gmtime if conv_tm else None)

    def _cmptime(self, cmp, cmpval, conv):
        for t in self.st_time():
            cmpval = cmp(cmpval, t)
        return cmpval if conv == None else conv(cmpval)

    # time helper

    P_CREATE = 0
    P_ACCESS = 1
    P_MODIFY = 2

    T_MODIFY = "m"
    T_ACCESS = "a"
    T_CREATE = "c"

    def st_time(self, wrap=False, when=None):
        t = None
        if when == None:
            # oder: create access modify
            t = self._stat.st_ctime, self._stat.st_atime, self._stat.st_mtime
            return FileStat.Time(*t) if wrap else t
        elif when == "m":
            t = self._stat.st_mtime
        elif when == "a":
            t = self._stat.st_atime
        elif when == "c":
            t = self._stat.st_ctime
        else:
            raise Exception("invalid", when)
        return t

    #

    def time(self, wrap=True):
        t = self.st_time(wrap=wrap)
        return t

    def amtime(self):
        cam = self.st_time()
        return cam[1], cam[2]

    def utctime(self, wrap=True):
        return self._convtime(time.gmtime, wrap=wrap)

    def gmtime(self, wrap=True):
        """deprecated, use utctime()"""
        # warnings.warn("use utctime()", DeprecationWarning, )
        return self.utctime(wrap=wrap)

    def localtime(self, wrap=True):
        # use always utc for computation
        # local time for display
        return self._convtime(time.localtime, wrap=wrap)

    def _convtime(self, conv, wrap=True):
        tm = [conv(t) for t in self.st_time()]
        return FileStat.Time(*tm) if wrap else tm

    # touch

    def touch_ux(self, amtime=None):
        return os.utime(self.name, times=amtime)

    @staticmethod
    def _default(v, d):
        return v if v != None else d

    def touch_am(self, atime=None, mtime=None):
        n = time.time()
        atime = self._default(atime, n)
        mtime = self._default(mtime, n)
        return atime, mtime

    def touch_a(self, atime=None):
        atime = self._default(atime, time.time())
        return atime, self._stat.st_mtime

    def touch_m(self, mtime=None):
        mtime = self._default(mtime, time.time())
        return self._stat.st_atime, mtime

    # explore

    def scandir(self, expand=True):
        self.stat()
        if not self.is_dir:
            raise Exception("not a folder")
        # todo use stat from scandir dir entry directly inconstructor
        mf = map(lambda x: FileStat(x.path, expand=expand), os.scandir(self.name))
        return mf

    def iglob(self, pattern=None, recursive=False, prefetch=False):
        self.stat()
        if not self.is_dir:
            raise Exception("not a folder")

        if pattern == None:
            pattern = "**" if recursive else "*"

        fit = FileStat(self.name) if pattern == None else self.clone().join([pattern])

        it = glob.iglob(fit.name, recursive=recursive)

        mf = map(lambda x: FileStat(x, prefetch=prefetch), it)
        return mf

    def files(self, expand=True):
        it = self.scandir(expand)
        f = filter(lambda x: x.stat() and x.is_file(), it)
        return f

    def folder(self, expand=True):
        it = self.scandir(expand)
        f = filter(lambda x: x.stat() and x.is_dir(), it)
        return f

    def walk(self, topdown=True, onerror=None, followlinks=False, wrap=True):
        it = os.walk(
            self.name, topdown=topdown, onerror=onerror, followlinks=followlinks
        )
        for e in it:
            if wrap:
                e = (
                    FileStat(e[0]),
                    [FileStat(e[0]).join([x]) for x in e[1]],
                    [FileStat(e[0]).join([x]) for x in e[2]],
                )
            yield e

    def find_empty_folder(self, wrap=False):
        empty = filter(
            lambda x: len(x[1]) == 0 and len(x[2]) == 0, self.walk(wrap=wrap)
        )
        return empty

    # manipulation

    def remove(self, dryrun=False):
        if self.exists() and dryrun == False:
            if self.is_file():
                os.remove(self.name)
            elif self.is_dir():
                os.rmdir(self.name)
            else:
                raise Exception("unsupported")

    def rename(self, name, dryrun=False):
        """renames a file in the same folder"""

        if name.find(os.sep) >= 0:
            raise Exception("wrong operation. use move instead")

        src = FileStat(self.name)
        if src.exists() == False:
            raise Exception("file dont exists", src.name)

        dest = FileStat().join([src.dirname(), name])

        if dest.name == src.name:
            raise Exception("same file", src.name)

        if dest.exists():
            raise Exception("file exists", dest.name)

        if dryrun == False:
            os.rename(src.name, dest.name)
            self.name = dest.name
            self.stat()

        return src.name, dest.name

    def move(self, dirname, dryrun=False, mkcopy=False):
        """moves the file to a different folder, keeping the name"""

        src = FileStat(self.name)
        if src.exists() == False:
            raise Exception("file dont exists", src.name)

        if src.is_file():
            dest = FileStat(dirname)
        elif src.is_dir():
            raise Exception("untested", src.name)
            # dest = FileStat().join([dirname,src.basename()])
        else:
            raise Exception("file type not supported")

        if dest.name == src.name:
            raise Exception("same file", src.name)

        if dest.exists():
            raise Exception("file exists", dest.name)

        if dryrun == False:
            dest.makedirs()
            if mkcopy is False:
                os.rename(src.name, dest.name)
            else:
                shutil.copy2(src.name, dest.name)
                # todo touch_ux

        self.name = dest.name
        self.stat()

        return src.name, dest.name

    def hash(self, hashfunc=None):
        return _get_file_hash(self.name, hashfunc=hashfunc)


class Hash(object):
    def __init__(self, hashfunc=None):
        if hashfunc is None:
            hashfunc = "sha512"
        self.hm = hashlib.new(hashfunc)

    def update(self, data):
        self.hm.update(data)

    def hexdigest(self):
        digest = self.hm.hexdigest()
        return digest


def _get_file_hash(fnam, blk_size=DEFAULT_BLOCK_SIZE, hashfunc=None):
    hm = Hash(hashfunc)
    with open(fnam, "rb") as f:
        while True:
            buf = f.read(blk_size)
            if len(buf) == 0:
                break
            hm.update(buf)
    digest = hm.hexdigest()
    return digest
