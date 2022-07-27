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
    imagemagik -resize
    resizes to 50% by default
    """
    args = get_argv(args)
    check_argv(args)

    with ArgsInAdapter(args) as fi:

        inp = fi.read()

        opts = opt_argv()
        size_ = pop_argv(opts, "50%")

        with ArgsOutAdapter(args) as fo:

            rc = procrun(
                args=["convert", "-", "-resize", size_, "-"],
                input=inp,
            )

            if rc.returncode > 0:
                raise Exception(rc)

            fo.write(rc.stdout)

            rc.stdout = None
            return rc


if __name__ == "__main__":
    # print(sys.argv)
    rc = convert()
