import sys
import os


class CtxTempFile(object):
    def __init__(self):
        self.files = set()

    def open(self, fnam, mode="r"):
        fd = open(fnam, mode=mode)
        for m in mode:
            if m in ["a", "+", "w"]:
                self.files.add(fnam)
                break
        return fd

    def close(self, fd):
        fd.close()

    def cleanup(self):
        for fnam in self.files:
            try:
                # print("rm", fnam)
                os.remove(fnam)
            except Exception as ex:
                pass
                # print("error remove", fnam, file=sys.stdout)
        self.files.clear()

    # use _always_ in with context block
    # so cleanup is performed automatically

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
