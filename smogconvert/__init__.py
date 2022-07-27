import sys
import os

MEDIA_SRC = "MEDIA_SRC"
FIRST_OPT_ARG = 3

from .adapter import STDIO, ArgsInAdapter, ArgsOutAdapter
from .convert import procrun


def get_argv(args=None):
    if args is None:
        args = sys.argv
    return args


def check_argv(args=None, err_ok=False):
    args = get_argv(args)
    _chk = len(args) < FIRST_OPT_ARG
    if err_ok:
        return _chk
    if _chk:
        raise Exception("wrong number of call parameter")


def opt_argv(args=None):
    args = get_argv(args)
    return args[FIRST_OPT_ARG:]


def pop_argv(opts, default=None):
    if opts:
        if len(opts) > 0:
            return opts.pop(0)
    return default


def merge_os_env(env=None):
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
