import sys
import os

from smogconvert import ArgsInAdapter, ArgsOutAdapter, check_argv


def convert(container=None):
    check_argv()

    print("--- env")

    for k, v in os.environ.items():
        print(k, v)

    print("--- argv")

    print(sys.argv)


if __name__ == "__main__":
    sys.exit(convert())
