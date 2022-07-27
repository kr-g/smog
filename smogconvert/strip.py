import sys
from smogconvert import (
    ArgsInAdapter,
    ArgsOutAdapter,
    get_argv,
    check_argv,
    opt_argv,
    procrun,
)


def convert(args=None, container=None):
    """
    imagemagik -strip
    drops all xmp metadata
    will reduce also size
    """
    args = get_argv(args)
    check_argv(args)

    with ArgsInAdapter(args) as fi:

        inp = fi.read()

        rc = procrun(
            args=["convert", "-", "-strip", "-"],
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
