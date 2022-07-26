import os


class CtxEnv(object):
    def __init__(self, env=None):
        self._env = None
        self._overlay = env

    def __enter__(self):
        self._env = dict(os.environ)
        if self._overlay:
            os.environ = self._overlay
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.environ = self._env

    def get(self, nam, default=None):
        return os.environ.setdefault(nam, default)
