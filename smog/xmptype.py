import itertools
import mimetypes

try:
    from .file import FileStat
except:
    from file import FileStat

mimetypes.init()

_mimes = set(
    filter(
        lambda x: x.split("/")[0] in ["audio", "image", "video"],
        mimetypes.types_map.values(),
    )
)

_candidates = list(map(lambda x: mimetypes.guess_all_extensions(x), _mimes))
_candidates += ["pdf"]

# this contains possible file extensions to check for xmp metadata

_guessed = set(map(lambda x: x[1:], itertools.chain.from_iterable(_candidates)))


def guess_xmp_ext(ext):
    global _guessed
    return ext in _guessed


def guess_xmp_fnam(fnam):
    f = FileStat(fnam)
    _, ext = f.splitext()
    return guess_xmp_ext(ext[1:])
