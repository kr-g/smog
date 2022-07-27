import sys
from smogconvert import (
    ArgsInAdapter,
    ArgsOutAdapter,
    get_argv,
    check_argv,
    opt_argv,
    pop_argv,
    procrun,
)


def convert(args=None, container=None):
    """
    imagemagik -thumbnail
    resizes to 64x64> by default
    """
    args = get_argv(args)
    check_argv(args)

    with ArgsInAdapter(args) as fi:

        inp = fi.read()

        opts = opt_argv()
        size_ = pop_argv(opts, "64x64>")

        rc = procrun(
            args=["convert", "-", "-thumbnail", size_, "-"],
            input=inp,
        )

        if rc.returncode > 0:
            raise Exception(rc)

    with ArgsOutAdapter(args) as fo:
        fo.write(rc.stdout)

    rc.stdout = None
    return rc


if __name__ == "__main__":
    # print(sys.argv)
    rc = convert()
