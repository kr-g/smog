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
        self.srcdir = srcdir
        self.repodir = repodir
        self.procdir = procdir

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


class CtxRunner(object):
    def __init__(self, ctx, input_iter):
        self.ctx = ctx
        self.input_iter = input_iter

        self.proc = None
        self.output = None

        self.errproc = []
        self.errout = []

    def config_run(self, proc, output, errprochndl=None, errouthndl=None):
        self.proc = proc
        self.output = output
        self.errhndl = errhandl if errhndl else self.errproc_handler
        self.errouthndl = errouthndl if errouthndl else self.errout_handler

    def run(self):
        for inp in self.input_iter():

            rc, err, ex = do_proc(inp)
            if ex:
                print(ex)
            if err:
                err = self.errhndl(err)
            if err or ex:
                continue

            rc, err, ex = do_output(inp)
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
