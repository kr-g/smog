import sys
from smogconvert import ArgsInAdapter, ArgsOutAdapter, check_argv


def convert(container=None):
    check_argv()

    with ArgsInAdapter() as fi:
        with ArgsOutAdapter() as fo:
            fo.write(fi.read())


if __name__ == "__main__":
    sys.exit(convert())
