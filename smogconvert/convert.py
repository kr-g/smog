import sys
import os
import subprocess
import importlib

import smogconvert as SmogConvert
from smogconvert.ctxenv import CtxEnv

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


def convert(args, input=None, container=None, env=None, open_external=True):

    _env = SmogConvert.merge_os_env(env)

    exprefnam = is_predefined(args[0])
    if not exprefnam:
        exprefnam = args[0]
        raise NotImplementedError()

    if open_external:
        _exec_ctx = get_call_context(args)
        _exec_ctx.extend([exprefnam, *args[1:]])

        if args[1] == SmogConvert.STDIO:
            inp_mode = subprocess.PIPE
        else:
            inp_mode = None

        if args[2] == SmogConvert.STDIO:
            cap_mode = True
        else:
            cap_mode = False

        rc = subprocess.run(
            args=_exec_ctx,
            stdin=inp_mode,
            input=input,
            env=_env,
            capture_output=cap_mode,
        )
    else:
        nargs = normalize_args(args)
        mod = importlib.import_module(SMOGCONV_NAME + "." + nargs[0])

        with CtxEnv(_env) as ctxenv:
            # bump env
            try:
                rc = mod.convert(nargs, container)
            except Exception as ex:
                print(ex, file=sys.stderr)
                rc = ex

    return rc


if __name__ == "__main__":
    z = {"zzz": 56657}
    for ot in [True, False]:
        rc = convert(
            [
                "copyfile.py",
                *sys.argv[1:],
            ],
            env=z,
        )
        print(rc)
