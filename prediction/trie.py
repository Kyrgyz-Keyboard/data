from typing import Iterable

from dataclasses import dataclass, field
from collections import defaultdict
from io import BytesIO
import itertools
import struct
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

#         L1 + 5 predictions
#         L1 + L2 + 5 predictions
#         L1 + L2 + L3 + 5 predictions
LAYERS = [None, 5, 5, 5]

assert None not in LAYERS[1:], 'All layers except the first must have a maximum size'


_DECODING_TABLE = (
    ',.:'
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    'ҢҮӨ'
    'ңүө'
)
ENCODING_TABLE = {letter: index.to_bytes(1, 'big') for index, letter in enumerate(_DECODING_TABLE, start=1)}
DECODING_TABLE = {index.to_bytes(1, 'big'): letter for index, letter in enumerate(_DECODING_TABLE, start=1)}


TrieNodeJson = tuple[int, dict[str, 'TrieNodeJson']]


@dataclass
class TrieNode:
    freq: int = 0
    children: dict[int, 'TrieNode'] = field(default_factory=lambda: defaultdict(TrieNode))

    def add(self, word_indices: list[int], index: int):
        if index == len(word_indices) - 1:
            self.children[word_indices[index]].freq += 1
        else:
            self.children[word_indices[index]].add(word_indices, index + 1)

    def dump(self, file_obj: BytesIO, word_indices: dict[str, int], layer: int = 0):
        file_obj.write(struct.pack('>I', self.freq))
        if layer == len(LAYERS):
            return

        sorted_children = sorted(self.children.items(), key=lambda x: x[1].freq, reverse=True)
        # print(layer, sorted_children)
        layer_size = LAYERS[layer] or len(sorted_children)

        for i in range(min(len(sorted_children), layer_size)):
            word_index, next_node = sorted_children[i]
            file_obj.write(struct.pack('>I', word_index))
            next_node.dump(file_obj, word_indices, layer + 1)

        if len(sorted_children) < layer_size:
            file_obj.write(struct.pack('>I', 0))

    def load(self, file_obj: BytesIO, word_indices: dict[str, int], layer: int = 0):
        self.freq = struct.unpack('>I', file_obj.read(4))[0]
        if layer == len(LAYERS):
            return

        layer_size = LAYERS[layer] or float('inf')

        index = 0
        while (word_index_bytes := file_obj.read(4)):
            word_index = struct.unpack('>I', word_index_bytes)[0]

            if word_index == 0:
                break

            next_node = TrieNode()
            next_node.load(file_obj, word_indices, layer + 1)
            self.children[word_index] = next_node

            index += 1
            if index == layer_size:
                break

    def to_json(self, words_indexed_reverse: dict[int, str]) -> TrieNodeJson:
        return (
            self.freq, {
                words_indexed_reverse[i]: child.to_json(words_indexed_reverse)
                for i, child in self.children.items()
                # if i >= WORD_INDEX_SHIFT
            }
        )


WORD_INDEX_SHIFT = 1  # + 1 beacuse index 0 means None


@dataclass
class Trie(TrieNode):
    words_indexed: dict[str, int] = field(default_factory=dict)

    def add(self, words: Iterable[str]):  # type: ignore[override]
        word_indices = [
            self.words_indexed.setdefault(word, len(self.words_indexed) + WORD_INDEX_SHIFT)
            for word in words
        ]
        # TODO: Can be optimized to len(word_indices) - 1 if we don't store 1-grams
        for slice_start in range(len(word_indices)):
            super().add(word_indices, slice_start)

    def dump(self, file_obj: BytesIO):  # type: ignore[override]
        # Write the amounf of words
        file_obj.write(struct.pack('>I', len(self.words_indexed)))

        # Write the words list
        for word in self.words_indexed:
            for letter in word:
                file_obj.write(ENCODING_TABLE[letter])
            file_obj.write(b'\x00')

        # Write the trie
        super().dump(file_obj, self.words_indexed)

    def load(self, file_obj: BytesIO) -> 'Trie':  # type: ignore[override]
        # Read the amount of words
        trie_size = struct.unpack('>I', file_obj.read(4))[0]

        # Read the words list
        counter = itertools.count(WORD_INDEX_SHIFT)
        for _ in range(trie_size):
            word = ''
            while (current_byte := file_obj.read(1)) != b'\x00':
                word += DECODING_TABLE[current_byte]
            self.words_indexed[word] = next(counter)

        super().load(file_obj, self.words_indexed)
        return self

    # Helper functions:

    def to_json(self) -> TrieNodeJson:  # type: ignore[override]
        words_indexed_reverse: dict[int, str] = {index: word for word, index in self.words_indexed.items()}
        return super().to_json(words_indexed_reverse)

    def dump_file(self, file_path: str):
        with open(mkpath(file_path), 'wb') as file_obj:
            self.dump(file_obj)  # type: ignore[arg-type]

    @classmethod
    def load_file(cls, file_path: str) -> 'Trie':
        with open(mkpath(file_path), 'rb') as file_obj:
            return cls().load(file_obj)  # type: ignore[arg-type]

    def fetch(self, words: list[str]) -> list[tuple[str, int]]:
        words_indexed_reverse: dict[int, str] = {index: word for word, index in self.words_indexed.items()}

        result = []
        cur_obj: TrieNode = self

        for word in words:
            if self.words_indexed[word] not in cur_obj.children:
                print(f'Word "{self.words_indexed[word]}" not found as a step')
                break

            cur_obj = cur_obj.children[self.words_indexed[word]]

            result.extend(
                [(words_indexed_reverse[prediction], node.freq) for prediction, node in cur_obj.children.items()]
            )

        return result


if __name__ == '__main__':
    import json

    file_obj = BytesIO()

    trie = Trie()

    # trie.add('one'.split())  # noqa
    # trie.add('one two'.split())  # noqa

    trie.add('lorem ipsum dolor sit'.split())  # noqa
    # trie.add('ipsum dolor sit amet'.split())  # noqa
    # trie.add('dolor sit amet consectetur'.split())  # noqa
    # trie.add('sit amet consectetur adipiscing'.split())  # noqa
    # trie.add('amet consectetur adipiscing elit'.split())  # noqa

    # print(json.dumps(trie.to_json(), indent=4, ensure_ascii=False))

    trie.dump(file_obj)

    file_obj.seek(0)

    new_trie = Trie().load(file_obj)

    print(json.dumps(new_trie.to_json(), indent=4, ensure_ascii=False))
