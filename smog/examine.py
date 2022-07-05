from .file import FileStat


def ifile(
    fpath,
    ext=None,
    pattern=None,
    recursive=False,
):

    fbase = FileStat(fpath)

    if ext != None and len(ext) > 0:
        ext = list(map(lambda x: "." + x.upper(), ext))
    else:
        ext = None

    for f in fbase.iglob(pattern=pattern, recursive=recursive, prefetch=True):

        if not f.is_file():
            continue

        _, fext = f.splitext()

        if ext:
            try:
                _ = ext.index(fext.upper())
            except:
                # ext not found
                continue

        yield f
