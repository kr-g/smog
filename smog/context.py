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

    # static
    def mksubpath(fnam, path):
        path = FileStat(path).name + FileStat.sep
        if not fnam.startswith(path):
            raise Exception("not on folder", path)
        return fnam[len(path) :]

    def norm_src_path(self, fnam):
        return Context.mksubpath(fnam, self.srcdir)

    def norm_repo_path(self, fnam):
        return Context.mksubpath(fnam, self.repodir)


class CtxProcessor(object):
    def reset(self, ctx):
        self.ctx = ctx

    def process(self, inp, err):
        raise NotImplementedError()


class CtxPipe(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.chain = []

    def add(self, ctx_proc):
        self.chain.append(ctx_proc)

    def reset(self):
        for cproc in self.chain:
            cproc.reset(ctx)

    def process(self, inp=None, err=None):
        for cproc in self.chain:
            inp, err = cproc.process(inp, err)
            if inp is None and err is None:
                break
