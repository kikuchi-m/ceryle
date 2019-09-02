import pathlib


def joinpath(*path):
    return str(pathlib.Path(*path))
