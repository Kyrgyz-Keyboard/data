import os


def mkpath(*paths: str) -> str:
    return os.path.normpath(os.path.join(*paths))


def write_file(path: str, data: str, append: bool = False):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as file:
        file.write(data)
