from contextlib import contextmanager, suppress, chdir
import sys
import os


def mkpath(*paths: str) -> str:
    return os.path.normpath(os.path.join(*paths))


class PathMagic:
    def __init__(self, source_file_path: str):
        self.source_file_directory = os.path.dirname(os.path.abspath(source_file_path))
        # sys.path.remove(self.source_file_directory)

    def __call__(self, *paths: str) -> str:
        return mkpath(self.source_file_directory, *paths)

    @contextmanager
    def import_from(self, import_from_path: str):
        sys.path.append(mkpath(self.source_file_directory, import_from_path))
        try:
            yield
        finally:
            with suppress(ValueError):
                sys.path.remove(mkpath(self.source_file_directory, import_from_path))

    @contextmanager
    def chdir(self, *paths: str):
        with chdir(mkpath(self.source_file_directory, *paths)):
            yield


def write_file(path: str, data: str, append: bool = False):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, ('a' if append else 'w'), encoding='utf-8') as file:
        file.write(data)
