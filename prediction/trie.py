from typing import Sequence, Iterable

from io import BytesIO
import itertools
import struct
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

# ======================================================================================================================

LAYERS = [(None, float('inf')), (10, 5), (5, 5), (5, 0)]


WORD_INDEX_SHIFT = 1  # + 1 because index 0 means None

_DECODING_TABLE = (
    ',.:'
    '0123456789'
    # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    # 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    # 'ҢҮӨ'
    'ңүө'
)

# ======================================================================================================================

ENCODING_TABLE = {letter: index.to_bytes(1, 'big') for index, letter in enumerate(_DECODING_TABLE, start=1)}
DECODING_TABLE = {index.to_bytes(1, 'big'): letter for index, letter in enumerate(_DECODING_TABLE, start=1)}


TrieNode = list[int, dict[int, 'TrieNode']]  # type: ignore
TrieNodeRepr = tuple[int, dict[str, 'TrieNodeRepr']]


# def _add(cur_data: dict[int, 'TrieNode'], word_indices: list[int], index: int):
#     if index == len(word_indices) - 1:
#         cur_data.setdefault(word_indices[index], [0, {}])[0] += 1
#     else:
#         _add(
#             cur_data.setdefault(word_indices[index], [0, {}])[1],
#             word_indices,
#             index + 1
#         )


def _sort(node: TrieNode):
    node[1] = dict(sorted(node[1].items(), key=lambda x: x[1][0], reverse=True))
    for child in node[1].values():
        _sort(child)


def _dump(cur_data: dict[int, 'TrieNode'], file_obj: BytesIO, words_indexed: dict[str, int], layer: int = 0):
    if layer == len(LAYERS):
        return

    for i, (word_index, (freq, next_node)) in enumerate(itertools.islice(cur_data.items(), LAYERS[layer][0])):
        file_obj.write(struct.pack('>I', word_index))
        file_obj.write(struct.pack('>I', freq))
        if i < LAYERS[layer][1]:
            _dump(next_node, file_obj, words_indexed, layer + 1)

    if len(cur_data) < (LAYERS[layer][0] or len(cur_data)):
        file_obj.write(struct.pack('>I', 0))


def _load(cur_data: dict[int, 'TrieNode'], file_obj: BytesIO, words_indexed: dict[str, int], layer: int = 0):
    if layer == len(LAYERS):
        return

    index = 0
    while (word_index_bytes := file_obj.read(4)):
        word_index = struct.unpack('>I', word_index_bytes)[0]

        if word_index == 0:
            break

        freq = struct.unpack('>I', file_obj.read(4))[0]
        next_node = [freq, {}]
        cur_data[word_index] = next_node
        if index < LAYERS[layer][1]:
            _load(next_node[1], file_obj, words_indexed, layer + 1)

        index += 1
        if index == LAYERS[layer][0]:
            break


class Trie:
    def __init__(self, all_words: Iterable[str]):
        self.words_indexed: dict[str, int] = {
            word: index
            for index, word in enumerate(all_words, start=WORD_INDEX_SHIFT)
        }
        self.data: dict[int, 'TrieNode'] = {}

    def add(self, words: Sequence[str]):
        # print(self.words_indexed)
        # TODO: Can be optimized to len(word_indices) - 1 if we don't store 1-grams
        for slice_start in range(len(words) - 1):
            cur_data = self.data
            for i in range(slice_start, len(words) - 1):
                cur_data = cur_data.setdefault(self.words_indexed[words[i]], [0, {}])[1]
            cur_data.setdefault(self.words_indexed[words[-1]], [0, {}])[0] += 1

    def dump(self, file_obj: BytesIO):
        # Write the amounf of words
        file_obj.write(struct.pack('>I', len(self.words_indexed)))

        # Write the words list
        for word in self.words_indexed:
            for letter in word:
                file_obj.write(ENCODING_TABLE[letter])
            file_obj.write(b'\x00')

        # Write the trie
        print('Sorting...')
        for node in self.data.values():
            _sort(node)
        print('Dumping...')
        _dump(self.data, file_obj, self.words_indexed)

    @classmethod
    def load(cls, file_obj: BytesIO) -> 'Trie':
        # Read the amount of words
        trie_size = struct.unpack('>I', file_obj.read(4))[0]

        # Read the words list
        words_indexed = []
        for _ in range(trie_size):
            word = ''
            while (current_byte := file_obj.read(1)) != b'\x00':
                word += DECODING_TABLE[current_byte]
            words_indexed.append(word)

        result = cls(words_indexed)

        # Read the trie
        _load(result.data, file_obj, result.words_indexed)
        return result

    # Helper functions (slow):

    def get_words_indexed_reverse(self) -> dict[int, str]:
        return {index: word for word, index in self.words_indexed.items()}

    def get_data(self) -> dict[str, 'TrieNodeRepr']:
        words_indexed_reverse = self.get_words_indexed_reverse()

        def convert_nodes(children: dict[int, 'TrieNode']) -> dict[str, 'TrieNodeRepr']:
            return {
                words_indexed_reverse[i]: (child[0], convert_nodes(child[1]))
                for i, child in children.items()
            }

        return convert_nodes(self.data)

    def dump_file(self, file_path: str):
        with open(mkpath(file_path), 'wb') as file_obj:
            self.dump(file_obj)  # type: ignore[arg-type]

    @classmethod
    def load_file(cls, file_path: str) -> 'Trie':
        with open(mkpath(file_path), 'rb') as file_obj:
            return cls.load(file_obj)  # type: ignore[arg-type]

    def fetch(self, words: list[str], max_results: int = 5) -> list[tuple[str, int]]:
        words_indexed_reverse = self.get_words_indexed_reverse()

        cur_data = self.data

        for word in words:
            if word not in self.words_indexed:
                print(f'Word "{word}" not found')
                return []
            if self.words_indexed[word] not in cur_data:
                print(f'Word "{word}" not found as a step')
                return []

            cur_data = cur_data[self.words_indexed[word]][1]

        return [
            (words_indexed_reverse[prediction], node[0])
            for prediction, node in itertools.islice(cur_data.items(), max_results)
        ]

    def encode_word(self, word: str) -> int:
        return self.words_indexed[word]

    def decode_word(self, word_index: int) -> str:
        return self.get_words_indexed_reverse()[word_index]


if __name__ == '__main__':
    import json

    # print(len(DECODING_TABLE))

    file_obj = BytesIO()

    trie = Trie(['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit'])

    # trie.add('one'.split())  # noqa
    # trie.add('one two'.split())  # noqa

    trie.add('lorem ipsum dolor adipiscing'.split())  # noqa
    trie.add('lorem ipsum dolor sit'.split())  # noqa
    trie.add('lorem ipsum dolor sit'.split())  # noqa
    trie.add('lorem ipsum dolor sit'.split())  # noqa
    trie.add('lorem ipsum dolor sit'.split())  # noqa
    # trie.add('ipsum dolor sit amet'.split())  # noqa
    # trie.add('dolor sit amet consectetur'.split())  # noqa
    # trie.add('sit amet consectetur adipiscing'.split())  # noqa
    # trie.add('amet consectetur adipiscing elit'.split())  # noqa

    # print(json.dumps(trie.get_data(), indent=4, ensure_ascii=False))

    trie.dump(file_obj)

    file_obj.seek(0)

    new_trie = Trie.load(file_obj)

    print(json.dumps(new_trie.get_data(), indent=4, ensure_ascii=False))
