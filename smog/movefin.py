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

    return fsrc.name, fstore.name


if __name__ == "__main__":

    for f, b, s in [
        ("~/Bilder/20220521.jpeg", "~/Bilder", "../../proc-media"),
        ("~/Bilder/20220521.jpeg", "~/Bilder", "../Bilder/"),
        ("~/Bilder/20220521.jpeg", "~/Bilder", make_timed_rel_store_path()),
        ("~/Bilder/20220521.jpeg", "~/Bilder", "//proc-media"),
        (
            "~/Bilder/20220508-0609 pfalz/IMG_20220508_172822.jpg",
            "~/Bilder",
            make_timed_rel_store_path(),
        ),
        (
            "~/Bilder/20220508-0609 pfalz/IMG_20220508_172822.jpg",
            "~/Bilder",
            "/proc-media",
        ),
    ]:
        try:
            rc = organize_move_processed_file(f, b, s)
            print(rc)
        except Exception as ex:
            print(ex)
