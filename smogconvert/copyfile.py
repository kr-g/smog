import sys
from smogconvert import ArgsInAdapter, ArgsOutAdapter, check_argv, opt_argv


def convert(container=None):
    check_argv()

    with ArgsInAdapter() as fi:
        with ArgsOutAdapter() as fo:
            fo.write(fi.read())

    print(opt_argv())


if __name__ == "__main__":
    sys.exit(convert())
