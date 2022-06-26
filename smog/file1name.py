import os


def make_unique_filename(filename, extname="Copy", sep=" "):

    cpyno = 1
    to_test = filename

    based, fnam = os.path.split(filename)
    fnam, ext = os.path.splitext(fnam)

    while os.path.exists(to_test):
        to_test = f"{fnam} ({extname}{sep}{cpyno}){ext}"
        to_test = os.path.join(based, to_test)
        cpyno = cpyno + 1

    return to_test
