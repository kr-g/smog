import sys
import os
import subprocess
import importlib

import smogconvert as SmogConvert
from smogconvert.ctxenv import CtxEnv

from smog.file import FileStat

SMOGCONV_FILE = SmogConvert.__file__
SMOGCONV_DIR = FileStat(SmogConvert.__file__).dirname()
SMOGCONV_NAME = SmogConvert.__name__

PYTHON = sys.executable
PYTHON_EXT = ".py"


def is_python_ctx(args):
    return args[0].endswith(PYTHON_EXT)


def normalize_args(args):
    if is_python_ctx(args):
        # strip away ".py" ending
        args[0], _ = FileStat(args[0]).splitext()
    return args


def get_call_context(args):
    return [PYTHON] if is_python_ctx(args) else []


def is_predefined(fnam):
    path = FileStat(SMOGCONV_DIR).join([fnam])
    if path.exists():
        if path.is_dir():
            raise Exception("is directory", path.name)
        return path.name


def procrun(args, input=None, env=None, capture_output=True, raise_err=True):
    rc = subprocess.run(
        args=args,
        input=input,
        env=env,
        capture_output=capture_output,
    )
    if raise_err and rc.returncode > 0:
        raise Exception("failed", rc)
    return rc


def convert(args, input=None, container=None, env=None, open_external=True):

    _env = SmogConvert.merge_os_env(env)

    exprefnam = is_predefined(args[0])
    if not exprefnam:
        exprefnam = args[0]
        raise NotImplementedError()

    if open_external:
        _exec_ctx = get_call_context(args)
        _exec_ctx.extend([exprefnam, *args[1:]])

        cap_mode = args[2] == SmogConvert.STDIO

        if container:
            print("external run. drop container", container)

        rc = procrun(
            args=_exec_ctx,
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
            container={"a": 1},
            open_external=ot,
        )
        print(rc)
        print("---")
    nargs = normalize_args(sys.argv)
    print(nargs)
