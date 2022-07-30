"""
this uses an already "maintained" requirements.txt files
and bumps the version numbers from currently installed
packages.
"""

import sys
import subprocess
import pip

from setuputil import load_requirements

debug = False


class Package(object):
    def __init__(self, spec):
        if spec.startswith("-e"):
            self.editable = True
            self.package = spec[spec.find("#egg=") + 5 :]
            self.version = None
        else:
            self.editable = False
            self.package = spec[: spec.find("==")]
            self.version = spec[spec.find("==") + 2 :]

    def __repr__(self):
        return (
            self.__class__.__name__
            + f"( {self.package}, {self.version}, {self.editable} )"
        )


def load_requirements_versions():
    packs = {}

    proc = subprocess.Popen(
        [
            "pip",
            "freeze",
        ],
        stdout=subprocess.PIPE,
    )

    while True:
        line = proc.stdout.readline()
        if len(line) == 0:
            break
        line = line.decode().strip()
        debug and print(line)
        p = Package(line)
        packs[p.package] = p

    requirements = load_requirements()
    print("loaded", requirements)

    def clr(x):
        p1 = x.find("==")
        p2 = x.find(">=")
        p3 = x.find(">")
        p = max(p1, p2)
        p = max(p, p3)
        if p < 0:
            return x
        return x[:p]

    req_cleared = list(map(lambda x: clr(x), requirements))

    print("cleared", req_cleared)

    new_req = []
    for p in req_cleared:
        pack = packs[p]
        if pack.version is None:
            new_req.append(f"{pack.package}")
            debug and print(new_req[-1:], "from editable", file=sys.stderr)
        else:
            new_req.append(f"{pack.package}=={pack.version}")
            debug and print(new_req[-1:])

    print("bumbed", new_req)

    new_requirements = "\n".join(new_req)

    return new_requirements


def save_requirements(new_requirements):
    with open("requirements.txt", "w") as f:
        f.write(new_requirements)


def bump_requirements():
    req_vers = load_requirements_versions()
    save_requirements(req_vers)


if __name__ == "__main__":
    bump_requirements()
