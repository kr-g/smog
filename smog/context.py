import sys

try:
    from .file import FileStat
except:
    from file import FileStat


class Context(object):
    def __init__(
        self,
        srcdir,
        repodir,
        procdir,
        db,
        move2repo=True,
        move2proc=False,
        hashtag=None,
        collection=None,
        cleartags=False,
        pattern=None,
        addext=None,
        recursive=True,
        excludedirs=None,
        scanlist=None,
        verbose=False,
        debug=False,
    ):
        self.srcdir = FileStat(srcdir).name
        self.repodir = FileStat(repodir).name
        self.procdir = FileStat(procdir).name if procdir else None

        self.pattern = pattern

        self.addext = addext if addext else []
        self.recursive = recursive

        self.excludedirs = excludedirs if excludedirs else []
        self.excludedirs.extend(
            [
                repodir,
                procdir,
            ]
        )

        self.scanlist = scanlist

        self.db = db

        self.move2repo = move2repo
        self.move2proc = move2proc

        self.hashtag = ["#" + x.lower() for x in hashtag] if hashtag else None
        self.cleartags = cleartags

        self.collection = collection

        self._verbose = verbose
        self._debug = debug

    # output management

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def vprint(self, *args):
        self._verbose and print(*args)

    def dprint(self, *args):
        self._debug and print("DEBUG", *args)

    def wprint(self, *args):
        print("WARNING", *args)

    def eprint(self, *args):
        print("ERROR", *args, file=sys.stderr)

    # static

    def mksubpath(fnam, path):
        path = FileStat(path).name + FileStat.sep
        if not fnam.startswith(path):
            raise Exception("not on folder", path)
        return fnam[len(path) :]

    #

    def norm_src_path(self, fnam):
        return Context.mksubpath(fnam, self.srcdir)

    def norm_repo_path(self, fnam):
        return Context.mksubpath(fnam, self.repodir)


class CtxProcessor(object):
    def reset(self, ctx):
        self.ctx = ctx

    def process(self, inp, err):
        # this does nothing
        return inp, err


class CtxTerm(CtxProcessor):
    def process(self, inp, err):
        self.ctx.vprint("terminating")
        if inp:
            self.ctx.dprint("done", inp)
        if err:
            self.ctx.eprint(err)
        return None, None


class CtxPrint(CtxProcessor):
    def process(self, inp, err):
        self.ctx.print(inp)
        return inp, err


class CtxStop(CtxProcessor):
    def process(self, inp, err):
        self.ctx.print("\nSTOPPING", inp)
        raise StopIteration()


class CtxPipe(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.chain = []

    def add(self, ctx_proc):
        self.chain.append(ctx_proc)

    def reset(self):
        for cproc in self.chain:
            cproc.reset(self.ctx)

    def process(self, inp=None, err=None):
        for cproc in self.chain:
            rc = cproc.process(inp, err)
            if rc is None:
                raise Exception("ctx flow None return", cproc.__class__.__name__)
            inp, err = rc
            if inp is None and err is None:
                break
