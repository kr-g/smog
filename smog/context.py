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
        dbmeta,
        pattern=None,
        addext=None,
        recursive=True,
        excludedirs=None,
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

        self.dbmeta = dbmeta

    def norm_repo_path(self, fnam):
        if not fnam.startswith(self.repodir):
            raise Exception("not on repo dir")
        return fnam[len(self.repodir) + 1 :]

    def norm_base_path(self, fnam):
        if not fnam.startswith(self.srcdir):
            raise Exception("not on src dir")
        return fnam[len(self.srcdir) + 1 :]


class CtxProcessor(object):
    def process(self, ctx, inp, err):
        raise NotImplementedError()


class CtxPipe(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.chain = []

    def add(self, ctx_proc):
        self.chain.append(ctx_proc)

    def process(self, inp=None):
        for cproc in self.chain:
            inp, err = cproc.process(self.ctx, inp, err)
            if inp is None and err is None:
                break
