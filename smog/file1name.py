import os


def imake_unique_filename(filename, extname="Copy", sep1=" ", sep2=" "):

    cpyno = 1

    based, fnam = os.path.split(filename)
    fnam, ext = os.path.splitext(fnam)

    while True:
        to_test = f"{fnam}{sep1}({extname}{sep2}{cpyno}){ext}"
        to_test = os.path.join(based, to_test)
        cpyno = cpyno + 1

        yield to_test


def make_unique_filename(filename, extname="Copy", sep1=" ", sep2=" "):

    to_test = filename

    newfnam = imake_unique_filename(filename, extname, sep1, sep2)

    while os.path.exists(to_test):
        to_test = next(newfnam)

    return to_test
