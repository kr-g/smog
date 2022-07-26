import sys

STDIO = "-"


class Adapter(object):
    def __init__(self):
        self.fd = None

    def open(self):
        if self.fd:
            raise Exception("already open")
        self.fd = self._open()

    def close(self):
        if self.fd:
            self._close(self.fd)
            self.fd = None

    def _open(self):
        pass

    def _close(self, fd):
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class InAdapter(Adapter):
    def read(self, blen=-1):
        return self.fd.read(blen)


class OutAdapter(Adapter):
    def write(self, byts):
        return self.fd.write(byts)


class FileAdapter(Adapter):
    def __init__(self, fnam, mode):
        Adapter.__init__(self)
        self.fnam = fnam
        self.mode = mode

    def set_mode(self, mode):
        self.mode = mode

    def _open(self):
        return open(self.fnam, self.mode)

    def _close(self, fd):
        fd.close()


class FileInAdapter(InAdapter, FileAdapter):
    def __init__(self, fnam, mode="rb"):
        InAdapter.__init__(self)
        FileAdapter.__init__(self, fnam, mode)


class FileOutAdapter(OutAdapter, FileAdapter):
    def __init__(self, fnam, mode="wb"):
        OutAdapter.__init__(self)
        FileAdapter.__init__(self, fnam, mode)


class StdinAdapter(InAdapter):
    def __init__(self):
        InAdapter.__init__(self)

    def _open(self):
        return sys.stdin.buffer


class StdoutAdapter(OutAdapter):
    def __init__(self):
        OutAdapter.__init__(self)

    def _open(self):
        return sys.stdout.buffer


class ArgAdapter(Adapter):
    def __init__(self, clsstd, clscust, argno, args=None):
        Adapter.__init__(self)

        if args is None:
            args = sys.argv

        if args[argno] == STDIO:
            self.ad = clsstd()
        else:
            self.ad = clscust(args[argno])

        self.args = args

    def optargs(self):
        return self.args[FIRST_OPT_ARG:]

    def _open(self):
        return self.ad._open()

    def _close(self, fd):
        return self.ad._close(fd)


class ArgOneInAdapter(InAdapter, ArgAdapter):
    def __init__(self, args=None):
        InAdapter.__init__(self)
        ArgAdapter.__init__(self, StdinAdapter, FileInAdapter, 1, args)


class ArgTwoOutAdapter(OutAdapter, ArgAdapter):
    def __init__(self, args=None):
        OutAdapter.__init__(self)
        ArgAdapter.__init__(self, StdoutAdapter, FileOutAdapter, 2, args)


# use this rather than own impl with e.g. argparse
# to support "in-proc" dynamic loading with import lib
# since convert call with container parameter


class ArgsInAdapter(ArgOneInAdapter):
    pass


class ArgsOutAdapter(ArgTwoOutAdapter):
    pass
