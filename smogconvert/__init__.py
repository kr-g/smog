import sys
import os

MEDIA_SRC = "MEDIA_SRC"
FIRST_OPT_ARG = 3

from .adapter import ArgsInAdapter, ArgsOutAdapter


def check_argv(err_ok=False):
    _chk = len(sys.argv) < FIRST_OPT_ARG
    if err_ok:
        return _chk
    if _chk:
        raise Exception("wrong number of call parameter")


def opt_argv():
    return sys.argv[FIRST_OPT_ARG:]


def merge_os_env(env):
    _env = dict(os.environ)
    if env:
        for k, v in env.items():
            if v:
                _env[k] = str(v)
            else:
                del _env[k]
    return _env


def get_original():
    return os.environ[MEDIA_SRC]


def set_original(fnam, env=None):
    if env is None:
        env = os.environ
    env[MEDIA_SRC] = fnam
