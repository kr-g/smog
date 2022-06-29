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


class CtxRunner(object):
    def __init__(self, ctx, input_iter):
        self.ctx = ctx
        self.input_iter = input_iter

        self.proc = None
        self.output = None

        self.errproc = []
        self.errout = []

    def config_run(self, proc, output, errhndl=None, errouthndl=None):
        self.proc = proc
        self.output = output
        self.errhndl = errhndl if errhndl else self.errproc_handler
        self.errouthndl = errouthndl if errouthndl else self.errout_handler

    def run(self):
        for inp in self.input_iter():

            rc, err, ex = self.do_proc(inp)
            if ex:
                print(ex)
            if err:
                err = self.errhndl(err)
            if err or ex:
                continue

            rc, err, ex = self.do_output(inp)
            if ex:
                print(ex)
            if err:
                err = self.errhndl(err)
            if err or ex:
                continue

        return self.errproc, self.errout

    def do_proc(self, inp):
        try:
            rc, err = self.proc(inp, self)
            return rc, err, None
        except Exception as ex:
            return None, inp, ex

    def errproc_handler(self, err):
        self.errproc.append(err)
        print("err", err)
        return True

    def do_output(self, inp):
        try:
            rc, err = self.output(inp, self)
            return rc, err, None
        except Exception as ex:
            return None, inp, ex

    def errout_handler(self, err):
        self.errout.append(err)
        print("err", err)
        return True
