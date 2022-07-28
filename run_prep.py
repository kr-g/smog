import os
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


pr(
    "",
)
pr("# all `smog` cmd-line options")
pr(
    "",
)

for idx, cmd in enumerate(
    [
        "",
        "config",
        "scan",
        "find",
        "col",
        "colman",
        "tag",
        "check",
        "hash",
    ]
):

    args = ["python3", "-m", "smog", cmd, "-h"]
    args = list(filter(lambda x: len(x), args))
    rc = subprocess.run(args, capture_output=True)

    if rc.returncode:
        raise Exception(rc)

    cmd = " ".join(args[2:-1])
    cmd_ = cmd.replace(" ", "_").replace("-", "")

    pr(
        "",
    )
    pr(f"## {cmd}")
    pr(
        "",
    )
    pr(
        f"run `{cmd} -h` for:",
    )
    pr(
        "",
    )
    lines = rc.stdout.decode().splitlines()
    for l in lines:
        pr(
            " " * 4 + l,
        )

    pr(
        "",
    )

    with open("README_CMDLINE.md", "w") as f:
        f.write(_doc)
