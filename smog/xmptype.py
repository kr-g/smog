# xmp specifications from adobe
# https://github.com/adobe/xmp-docs

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
_candidates += [
    [".pdf", ".odf"],
    # XMPSpecificationPart3.pdf
    [
        ".AI",
        ".PS",
        ".EPS",
        ".INDD",
        ".INDT",
        ".DNG",
        ".CRW",
        ".ERF",
        ".X3F",
        ".3FR",
        ".KDC",
        ".MOS",
        ".MFW",
        ".MRW",
        ".NEF",
        ".RW2",
        ".PEF",
        ".CR2",
        ".RAF",
        ".FFF",
        ".DCR",
        ".RWL",
        ".MEF",
        ".ORF",
        ".ORF",
        ".RAW",
        ".IIQ",
        ".SRW",
        ".SRF",
        ".ARW",
        ".SR2",
        ".IFF",
        ".RIFF",
    ],
]

# this contains possible file extensions to check for xmp metadata

_guessed = itertools.chain.from_iterable(_candidates)
_guessed = set(map(lambda x: x.lower(), _guessed))


def dump_guessed():
    [
        print(x, end="\n" if (i + 1) % 10 == 0 else "\t")
        for i, x in enumerate(sorted(_guessed))
    ]


def guess_xmp_ext(ext):
    global _guessed
    return ext.lower() in _guessed


def guess_xmp_fnam(fnam):
    f = FileStat(fnam)
    _, ext = f.splitext()
    return guess_xmp_ext(ext)
