import os


class CtxEnv(object):
    def __init__(self):
        self._env = None

    def __enter__(self, env=None):
        self._env = dict(os.environ)
        if env:
            os.environ = env
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.environ = self._env

    def get(self, nam, default=None):
        return os.environ.setdefault(nam, default)
