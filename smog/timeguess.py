import time
import re


def clr_spec(s, spec=":_.- "):
    s = [x for x in s if x not in spec]
    return "".join(s)


_patterns = [
    r".*([0-9]{8})[_-]([0-9]{6}).*",
    r".*([0-9]{4}[:.-][0-9]{2}[:.-][0-9]{2})[_ -]([0-9]{2}[:.-][0-9]{2}[:.-][0-9]{2}).*",
    r".*[_ -]([0-9]{8})([0-9]{6}).*",
]

_regex = [re.compile(x) for x in _patterns]


def tm_guess_from_fnam(fnam):
    for regex in _regex:
        match = regex.match(fnam)
        if match:
            try:
                date_, time_ = match.group(1), match.group(2)
                date_ = clr_spec(date_)
                time_ = clr_spec(time_)
                tm = time.strptime(date_ + " " + time_, "%Y%m%d %H%M%S")
                return tm
            except:
                pass


if __name__ == "__main__":
    fnams = [
        "IMG_20220316_154719.jpg",
        "IMG_2022:03:16_15:47:19.jpg",
        "IMG_2022:03:16 15:47:19.jpg",
        "IMG_2022:03:16-15:47:19.jpg",
        "IMG_20220316_124347178_20220316125225.jpg",
    ]
    for fnam in fnams:
        print(tm_guess_from_fnam(fnam))
