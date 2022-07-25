import sys
import os
import subprocess
import importlib

import smogconvert as SmogConvert

SMOGCONV_FILE = SmogConvert.__file__
SMOGCONV_NAME = SmogConvert.__name__

PYTHON = sys.executable
PYTHON_EXT = ".py"


def is_python_ctx(args):
    return args[0].endswith(PYTHON_EXT)


def normalize_args(args):
    if is_python_ctx(args):
        args[0] = args[0][:-3]
    return args


def get_call_context(args):
    return [PYTHON] if is_python_ctx(args) else []


def is_predefined(fnam):
    path = os.path.join(os.path.dirname(SMOGCONV_FILE), fnam)
    if os.path.exists(path):
        if os.path.isdir(path):
            raise Exception("is directory", path)
        return path


def convert(args, container=None, env=None, open_external=True):

    _bak_env = dict(os.environ)
    _env = SmogConvert.merge_os_env(env)

    exprefnam = is_predefined(args[0])
    if not exprefnam:
        raise NotImplementedError()

    if open_external:
        _exec_ctx = get_call_context(args)
        _exec_ctx.extend([exprefnam, *args[1:]])
        rc = subprocess.run(args=_exec_ctx, env=_env, capture_output=True)
    else:
        args = normalize_args(args)
        mod = importlib.import_module(SMOGCONV_NAME + "." + args[0])
        # bump argv
        bak_argv = sys.argv
        sys.argv = args
        # bump env
        os.environ = _env
        #
        rc = mod.convert(container)
        # roll back
        sys.argv = bak_argv
        # os.environ = _bak_env

    return rc
