import os
import time

try:
    from .file import FileStat
except:
    from file import FileStat


def make_timed_rel_store_path(prefix="proc-media", incl_tm=False):
    tm = time.strftime(
        "%Y-%m-%d" + (" %H:%M" if incl_tm else ""), time.localtime(time.time())
    )
    store = f"{prefix} {tm}"
    return store


def organize_move_processed_file(src, base, rel_store):
    fsrc = FileStat(src)
    _base = FileStat(base).name + os.sep
    fstore = FileStat(base).join(rel_store.split(os.sep))

    relp = fsrc.name
    if not relp.startswith(_base):
        raise Exception("wrong base folder", relp, "base", _base)

    if not fstore.name.startswith(_base):
        raise Exception(
            "wrong relative folder. must be a subfolder inside base folder.",
            relp,
            "base",
            _base,
        )

    relp = relp[len(_base) :]
    fstore = fstore.join([relp])

    if fstore.name == fsrc.name:
        raise Exception(
            "store identical. must be a subfolder inside base folder.",
            fstore.name,
            "base",
            _base,
        )

    clash = fstore.exists()

    return fsrc.name, fstore.name, clash
