import sys
from smogconvert import ArgsInAdapter, ArgsOutAdapter, get_argv, check_argv, opt_argv

from PIL import Image
from io import BytesIO


def convert(args=None, container=None):
    """
    converts to jpeg format
    drops all xmp metadata
    will reduce also size
    """
    args = get_argv(args)
    check_argv(args)

    with ArgsInAdapter(args) as fi:

        inp = fi.read()

        im = Image.open(BytesIO(inp))

        outp = BytesIO()
        im.convert("RGB").save(outp, "jpeg")

        byts = outp.getbuffer().tobytes()

        with ArgsOutAdapter(args) as fo:
            fo.write(byts)


if __name__ == "__main__":
    # print(sys.argv)
    sys.exit(convert())
