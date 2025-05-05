from typing import TextIO

import json
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


Trie = dict[str, 'Trie' | int]


def dump(trie: Trie, file_obj: TextIO):
    file_obj.write(json.dumps(trie, ensure_ascii=False, indent=2))


def dump_file(trie: Trie, file_path: str):
    with open(mkpath(file_path), 'w', encoding='utf-8') as file_obj:
        dump(trie, file_obj)


def load(file_obj: TextIO) -> Trie:
    return json.loads(file_obj.read())


def load_file(file_path: str) -> Trie:
    with open(mkpath(file_path), 'r', encoding='utf-8') as file_obj:
        return load(file_obj)
