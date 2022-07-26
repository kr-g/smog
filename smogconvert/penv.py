import sys
import os

from smogconvert import ArgsInAdapter, ArgsOutAdapter, get_argv, check_argv, opt_argv


def convert(args=None, container=None):
    args = get_argv(args)
    check_argv(args)

    print("--- env")

    for k, v in os.environ.items():
        print(k, v)

    print("--- argv")

    print(opt_argv(args))


if __name__ == "__main__":
    sys.exit(convert())
