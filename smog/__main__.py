import sys
from .smog import main_func


def main():
    rc = main_func()
    return rc


if __name__ == "__main__":
    sys.exit(main())
