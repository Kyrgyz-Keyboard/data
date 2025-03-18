import os


def mkpath(*paths: str) -> str:
    return os.path.normpath(os.path.join(*paths))
