import sys
from smogconvert import ArgsInAdapter, ArgsOutAdapter, get_argv, check_argv, opt_argv


def convert(args=None, container=None):
    args = get_argv(args)
    check_argv(args)

    with ArgsInAdapter(args) as fi:
        with ArgsOutAdapter(args) as fo:
            fo.write(fi.read())

    print(opt_argv(args))


if __name__ == "__main__":
    # print(sys.argv)
    sys.exit(convert())
