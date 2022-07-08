import time
import re

try:
    from .file import FileStat
except:
    from file import FileStat


class PreludeException(Exception):
    pass


class PreludeDateException(PreludeException):
    pass


class PreludeTimeException(PreludeException):
    pass


MEMO_VERSION = 1

S_VERSION = "version"
S_DATE = "date"
S_TIME = "time"
S_REFER = "refer"
S_NL = "\n"


def findblank(s):
    p1 = s.find(" ")
    p2 = s.find("\t")
    p = max(p1, p2)
    return p


def split_strip(s, p):
    if p < 0:
        return s.strip(), ""
    return s[:p].strip(), s[p:].strip()


def startswith_and_split(s, cmp):
    s = s.strip()
    p = findblank(s)
    h, t = split_strip(s, p)
    return h == cmp, h, t


def is_commented(s):
    if len(s) > 0:
        return s[0] in ["-", "#"]
    return False


#

_hash_regex = re.compile(r"(#[a-zA-Z0-9_+-]+)")


def ihashtag(tx):
    match = _hash_regex.finditer(tx)
    for i in match:
        yield i.group(0)


def hashtag(tx):
    return list(ihashtag(tx))


#


class Memo(object):

    EXT = ".smf"
    MIME = "application/simple-memo"

    def __init__(self, fnam):
        self.fnam = fnam
        self._head = []
        self._config = {}
        self._derived = set()

        self.body_idx = None
        self._body = None

        self._dirty = False

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join([str(k) + "=" + str(v) for k, v in self._config.items()])
            + ")"
        )

    # read the memo header meta

    def open(self, reset_head=True):
        with open(self.fnam) as f:
            while True:
                ln = f.readline()

                if len(ln) in [0, 1]:
                    # stops at end of header, or file
                    self.body_idx = f.tell()
                    break

                self._head.append(ln.strip())

        self._parse_header()

        if reset_head:
            self._head.clear()

        return self

    def close(self):
        if self.is_dirty():
            print("content not saved")

    def is_dirty(self, dirty=None):
        if dirty != None:
            self._dirty = dirty
        return self._dirty

    # process header

    def _parse_header(self):
        self._parse_header_prelude()
        print(self._head)
        for h in self._head:
            self._parse_head(h)

    # prelude header

    def _parse_header_prelude(self):
        for f, e in [
            (self._parse_version, None),
            (self._parse_date, PreludeDateException),
            (self._parse_time, PreludeTimeException),
        ]:
            if f(self._head[0]):
                self._head.pop(0)
            elif e:
                raise e()
        return

    def _parse_version(self, s):
        v, s = self._get_strip_head(S_VERSION, s)
        if v:
            s = int(s)
            if s < 1 or s > MEMO_VERSION:
                raise Exception("version number")
            self._config[v] = s
            return True
        else:
            self._config[S_VERSION] = MEMO_VERSION

    def _parse_date(self, s):
        s = s.strip()
        d = None

        _cmp, _h, _t = startswith_and_split(s, S_DATE)
        if _cmp:
            s = _t
        for df in [
            "%d.%m.%y",
            "%d.%m.%Y",
            "%Y.%m.%d",
            "%y.%m.%d",
        ]:
            try:
                d = time.strptime(s, df)[0:3]
                break
            except:
                pass

        if d != None:
            self._config[S_DATE] = d
            return True

    def _parse_time(self, s):
        s = s.strip()
        d = None

        _cmp, _h, _t = startswith_and_split(s, S_TIME)
        if _cmp:
            s = _t
        for df in [
            "%H:%M:%S",
            "%H:%M",
        ]:
            try:
                d = time.strptime(s, df)[3:6]
                break
            except:
                pass

        if d != None:
            self._config[S_TIME] = d
            return True

    # other header

    def _parse_refer(self, s):
        r, s = self._get_strip_head(S_REFER, s)
        if r:
            # todo
            self._derived.add(S_REFER + "_org")
            self._derived.add(S_REFER + "_abs")
            #
            self._config_add(r + "_org", s)
            s = s.strip("\"'")
            self._config_add(r, s)
            self._config_add(r + "_abs", FileStat.expandpath(s))
            return True

    def _parse_head(self, s):

        if is_commented(s):
            return

        if self._parse_refer(s):
            return

        r, s = self._get_strip_head(None, s)
        if r:
            self._config_add(r, s)
            return

    # general

    def _config_add(self, k, v):
        if k not in self._config:
            self._config[k] = []
        if v:
            self._config[k].append(v.strip())

    def _get_strip_head(self, h, s):
        if h:
            _cmp, _h, _t = startswith_and_split(s, h)
            if _cmp:
                return _h, _t
        else:
            try:
                pos = findblank(s)
                return split_strip(s, pos)
            except:
                return s, None
        return None, s

    def _read_body(self):
        with open(self.fnam) as f:
            f.seek(self.body_idx)
            return f.read()

    #

    def read(self):
        self._body = self._read_body()
        return self

    def body(self):
        return self._body

    def set_body(self, body):
        self._dirty = True
        self._body = body

    def has_head(self, hdr):
        return hdr in self._config

    def head(self, hdr):
        return self._config.get(hdr)

    def set_head(self, key, val):
        self._dirty = True
        self._config_add(key, str(val))

    def headers(self):
        return self._config

    #

    def get_str_head(self):

        prelude = [S_VERSION, S_DATE, S_TIME]
        prelude_fmt = [None, "%d.%m.%Y", "%H:%M:%S"]

        m = self._get_str_prelude(prelude, prelude_fmt)

        keys = self._config.keys()

        keys = keys - set(prelude)
        keys = keys - self._derived
        keys = sorted(keys)

        # flatten header
        for k in keys:
            for v in self.head(k):
                m += k + " " + str(v)
                m += S_NL

        return m

    def _get_str_prelude(self, pre, fmt):

        m = ""

        for p, f in zip(pre, fmt):
            pre = ""
            v = self.head(p)
            if f:
                if type(v) == time.struct_time:
                    v = time.strftime(f, v)
                else:
                    pre = "-"
                    v = ""
            m += pre + p + " " + str(v) + S_NL

        return m
