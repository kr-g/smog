import sys
import os
import re
import subprocess

# create markdown of cmd-line

_doc = ""


def pr(*args):
    global _doc
    d = ""
    for s in args:
        _doc += d
        _doc += s
        d = "\t"

    _doc += "\n"


pr("")
pr("# all `smog` cmd-line options")
pr("")


args = ["python3", "-m", "smog", "-h"]
rc = subprocess.run(args, capture_output=True)
if rc.returncode:
    raise Exception(rc)

s = rc.stdout.decode()

_regex = r"{(.*)}"
matches = re.finditer(_regex, s, re.MULTILINE)

scancmd = [""]

for m in matches:
    scancmd.extend(m.group(1).split(","))

print("found", scancmd)

for idx, cmd in enumerate(scancmd):

    args = ["python3", "-m", "smog", cmd, "-h"]
    args = list(filter(lambda x: len(x), args))
    rc = subprocess.run(args, capture_output=True)

    if rc.returncode:
        raise Exception(rc)

    cmd = " ".join(args[2:-1])
    cmd_ = cmd.replace(" ", "_").replace("-", "")

    pr("")
    pr(f"## {cmd}")
    pr("")
    pr(f"run `{cmd} -h` for help")
    pr("")
    lines = rc.stdout.decode().splitlines()
    for line in lines:
        pr(" " * 4 + line)

    pr("")

    with open("README_CMDLINE.md", "w") as f:
        f.write(_doc)
