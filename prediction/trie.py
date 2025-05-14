from typing import Sequence, Iterable, Generator

from math import log2, ceil
from io import BytesIO
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

# ======================================================================================================================

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


#               freq         is_stem  word_index
TrieNode = list[int, dict[tuple[bool, int], 'TrieNode']]  # type: ignore[type-arg]
TrieNodeRepr = tuple[int, dict[str, 'TrieNodeRepr']]

RETURN_MARKER = 1 << 7
STEM_MARKER = 1 << 6

RETURN_MARKER_WHOLE = RETURN_MARKER << 16
STEM_MARKER_WHOLE = STEM_MARKER << 16

INFINITY = int(1e9)


def _prepare(node: TrieNode, words_used: set[int], min_freq: int = 0, max_results: int = INFINITY):
    # Step 1: Remove nodes with freq < min_freq

    to_remove = []
    for key, next_node in node[1].items():
        _prepare(next_node, words_used, min_freq, max_results)
        node[0] += next_node[0]
        if next_node[0] < min_freq:
            to_remove.append(key)

    for key in to_remove:
        del node[1][key]

    # Step 2: Remove eccessive nodes, keep at least max_results non-stem nodes

    # Sort frequences for non-stem and empty nodes
    tmp_freq = sorted((
        freq
        for (is_stem, _), (freq, next_node_children) in node[1].items()
        if not is_stem and not next_node_children
    ))
    if max_results < len(tmp_freq):
        tmp_freq_threshold = tmp_freq[-max_results]

        to_remove = []
        for (is_stem, word_index), (freq, next_node_children) in node[1].items():
            if not is_stem and not next_node_children and freq < tmp_freq_threshold:
                to_remove.append((is_stem, word_index))

        for key in to_remove:
            del node[1][key]

    # Step 3: Record used words
    for (_, word_index) in node[1].keys():
        words_used.add(word_index)


def _dump(
    cur_data: dict[tuple[bool, int], 'TrieNode'],
    file_obj: BytesIO,
    new_index_mapping: dict[int, int],
    layer: int = 1
):
    for (is_stem, word_index), (_, next_node) in sorted(
        cur_data.items(),
        key=lambda x: x[1][0],
        reverse=True
    ):
        # Set first bit of the first byte of byte_repr to 1 if is_stem else 0:
        word_index = new_index_mapping[word_index]
        if is_stem:
            word_index |= STEM_MARKER_WHOLE

        file_obj.write(int.to_bytes(word_index, 3, 'big'))
        # file_obj.write(int.to_bytes(freq, 4, 'big'))
        if layer < Trie.MAX_LAYERS:
            _dump(next_node, file_obj, new_index_mapping, layer + 1)

    # pos = file_obj.tell()
    # return_amount = 1
    # if pos:
    #     file_obj.seek(pos - 1)
    #     last_byte = file_obj.read(1)

    #     if last_byte[0] & RETURN_MARKER:  # Is return marker
    #         val = last_byte[0] & ~RETURN_MARKER
    #         return_amount = val + 1
    #         file_obj.seek(pos - 1)
    #     else:
    #         file_obj.seek(pos)

    # file_obj.write(bytes([RETURN_MARKER | return_amount]))  # New return marker

    file_obj.write(RETURN_MARKER.to_bytes(1, 'big'))  # New return marker


# def _load(
#     cur_data: dict[tuple[bool, int], 'TrieNode'],
#     file_obj: BytesIO,
#     layer: int = 1
# ):
#     while (word_index_byte1 := file_obj.read(1)):
#         if word_index_byte1[0] & RETURN_MARKER:
#             # how_much_return = word_index_byte1[0] & ~RETURN_MARKER
#             # return how_much_return - 1
#             return

#         is_stem = bool(word_index_byte1[0] & STEM_MARKER)

#         word_index = struct.unpack('>I', b'\x00' + bytes([word_index_byte1[0] & ~STEM_MARKER]) + file_obj.read(2))[0]

#         # freq = struct.unpack('>I', file_obj.read(4))[0]
#         # next_node: TrieNode = [freq, {}]
#         next_node: TrieNode = [0, {}]
#         cur_data[(is_stem, word_index)] = next_node
#         if layer < Trie.MAX_LAYERS:
#             _load(next_node[1], file_obj, layer + 1)
#             # how_much_return = _load(next_node[1], file_obj, layer + 1)
#             # if how_much_return:
#             #     return how_much_return - 1

#     # return 0


class Trie:
    MAX_LAYERS = 4

    def __init__(
        self,
        all_words: Iterable[str],
        apertium_mapper: dict[str, str] | None = None
    ):
        self.apertium_mapper = apertium_mapper or {}
        self.words_indexed: dict[str, int] = {
            word: index
            for index, word in enumerate(all_words)
        }
        self.words_indexed_reverse: dict[int, str] = {
            index: word
            for word, index in self.words_indexed.items()
        }

        words_count_bits = ceil(log2(len(self.words_indexed)))
        # Reserved bits: 3
        # 24 - 2 = 22
        assert words_count_bits <= 22, f'Words count should be not more than 22 bits: currently {words_count_bits} bits'
        print(f'Trie intialized with {len(self.words_indexed):,d} words ({ceil(log2(len(self.words_indexed)))} bits)')

        assert Trie.MAX_LAYERS < 128, 'Max layers should be less than 128 for the return counter to work'

        self.data: dict[tuple[bool, int], 'TrieNode'] = {}

    def add(self, words: Sequence[str]):
        if words[-1] not in self.words_indexed:
            return

        for i in range(len(words) - 1):
            if words[i] not in self.words_indexed and words[i] not in self.apertium_mapper:
                return

        for slice_start in range(len(words) - 1):
            cur_data = self.data
            for i in range(slice_start, len(words) - 1):
                cur_data = cur_data.setdefault(
                    (
                        words[i] in self.apertium_mapper,
                        self.words_indexed[self.apertium_mapper.get(words[i], words[i])]
                    ),
                    [0, {}]
                )[1]

            cur_data.setdefault((False, self.words_indexed[words[-1]]), [0, {}])[0] += 1

    def dump(self, file_obj: BytesIO, min_freq: int = 0, max_results: int = 5):
        print('Preparing trie for dumping...')
        words_used: set[int] = set()
        _prepare([0, self.data], words_used, min_freq, max_results)

        print('Words used: ', len(words_used))

        print('Removing first layer nodes that have empty second layer...')
        to_remove = []
        for key, next_node in self.data.items():
            if not next_node[1]:
                to_remove.append(key)
        for key in to_remove:
            del self.data[key]

        print('Generating new index mapping...')
        new_index_mapping = {
            old_index: new_index
            for new_index, old_index in enumerate(words_used)
        }

        print('Dumping words...')
        file_obj.write(len(words_used).to_bytes(3, 'big'))
        for word in words_used:
            for letter in self.words_indexed_reverse[word]:
                file_obj.write(ENCODING_TABLE[letter])
            file_obj.write(b'\x00')

        # Write the trie
        print('Dumping trie...')
        _dump(self.data, file_obj, new_index_mapping)

    @classmethod
    def load(cls, file_obj: BytesIO) -> 'Trie':
        # Read the amount of words
        trie_size = int.from_bytes(file_obj.read(3), 'big')

        # Read the words list
        words_indexed = []
        for _ in range(trie_size):
            word = []
            while (current_byte := file_obj.read(1)) != b'\x00':
                word.append(DECODING_TABLE[current_byte])
            words_indexed.append(''.join(word))

        result = cls(words_indexed)

        # Read the trie
        stack = [(result.data, 1)]
        while stack:
            cur_data, layer = stack[-1]

            while True:
                word_index_byte1 = file_obj.read(1)[0]

                if word_index_byte1 & RETURN_MARKER:
                    stack.pop()
                    break

                is_stem = bool(word_index_byte1 & STEM_MARKER)
                word_index = ((word_index_byte1 & ~STEM_MARKER) << 16) | int.from_bytes(file_obj.read(2), 'big')

                # freq = int.from_bytes(file_obj.read(4), 'big')
                # next_node: TrieNode = [freq, {}]
                next_node: TrieNode = [0, {}]
                cur_data[(is_stem, word_index)] = next_node
                if layer < Trie.MAX_LAYERS:
                    stack.append((next_node[1], layer + 1))
                    break

        return result

    # Helper functions (slow):

    def get_data(self, data: dict[tuple[bool, int], 'TrieNode'] | None = None) -> dict[str, 'TrieNodeRepr']:
        return {
            self.words_indexed_reverse[word_index] + f' ({is_stem})': (child[0], self.get_data(child[1]))
            for (is_stem, word_index), child in (data if data is not None else self.data).items()
        }

    def dump_file(self, file_path: str, *args, **kwargs):
        with open(mkpath(file_path), 'wb+') as file_obj:
            self.dump(file_obj, *args, **kwargs)  # type: ignore[arg-type]

    @classmethod
    def load_file(cls, file_path: str, *args, **kwargs) -> 'Trie':
        with open(mkpath(file_path), 'rb') as file_obj:
            return cls.load(file_obj, *args, **kwargs)  # type: ignore[arg-type]

    def fetch(
        self,
        words: list[tuple[str, str]],
        max_results: int = 10,
        log_enabled: bool = False
    ) -> Generator[tuple[int, int, bool, str], None, None]:

        def log(*args, **kwargs):
            if log_enabled:
                print(*args, **kwargs)

        def fetch_inner(
            cur_data: dict[tuple[bool, int], 'TrieNode'],
            start_index: int
        ) -> Generator[tuple[tuple[bool, int], int], None, None]:

            if start_index == len(words):
                print('Results:', [(key, freq) for key, (freq, _) in cur_data.items()])
                for key, (freq, _) in cur_data.items():
                    yield key, freq
                return

            word, apertium_word = words[start_index]

            if apertium_word in self.words_indexed:
                if (True, self.words_indexed[apertium_word]) in cur_data:
                    log(f'Word found on layer (apertium): "{apertium_word}"')
                    yield from fetch_inner(
                        cur_data[(True, self.words_indexed[apertium_word])][1],
                        start_index + 1
                    )
                else:
                    log(f'Word not found on layer (apertium): "{apertium_word}"')
            else:
                log(f'Unknown word (apertium): "{apertium_word}"')

            if word in self.words_indexed:
                if (False, self.words_indexed[word]) in cur_data:
                    log(f'Word found on layer (normal): "{word}"')
                    yield from fetch_inner(
                        cur_data[(False, self.words_indexed[word])][1],
                        start_index + 1
                    )
                else:
                    log(f'Word not found on layer (normal): "{word}"')
            else:
                log(f'Unknown word: "{word}"')

        raw_results: list[tuple[int, int, bool, int]] = []
        for layers_num in range(min(len(words) + 1, Trie.MAX_LAYERS), 1, -1):
            log(layers_num, len(words) - layers_num + 1)
            raw_results.extend(
                (layers_num, freq, is_stem, prediction)
                for (is_stem, prediction), freq in fetch_inner(self.data, len(words) - layers_num + 1)
            )

        # Results are naturally sorted by descending path length and then by descending frequency
        distinct_results: set[tuple[bool, str]] = set()

        # First yield not stems
        for layers_num, freq, is_stem, prediction in raw_results:
            if len(distinct_results) == max_results:
                return
            if not is_stem and (False, self.words_indexed_reverse[prediction]) not in distinct_results:
                distinct_results.add((False, self.words_indexed_reverse[prediction]))
                yield (layers_num, freq, False, self.words_indexed_reverse[prediction])

        # Then yeild stems
        for layers_num, freq, is_stem, prediction in raw_results:
            if len(distinct_results) == max_results:
                return
            if is_stem and (True, self.words_indexed_reverse[prediction]) not in distinct_results:
                distinct_results.add((True, self.words_indexed_reverse[prediction]))
                yield (layers_num, freq, True, self.words_indexed_reverse[prediction])

    def word2index(self, word: str) -> int:
        return self.words_indexed[word]

    def index2word(self, word_index: int) -> str:
        return self.words_indexed_reverse[word_index]


if __name__ == '__main__':
    import json

    # print(len(DECODING_TABLE))

    file_obj = BytesIO()

    trie = Trie(
        ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'aloha', 'hola'],
        {
            'ipsum': 'ip',
            'sit': 'si'
        }
    )

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

    trie.add('lorem ipsum aloha'.split())  # noqa
    trie.add('lorem ipsum aloha'.split())  # noqa
    trie.add('lorem ipsum aloha'.split())  # noqa
    # trie.add('lorem ipsum aloha'.split())  # noqa

    trie.add('lorem ipsum hola'.split())  # noqa
    trie.add('lorem ipsum hola'.split())  # noqa
    trie.add('lorem ipsum hola'.split())  # noqa
    trie.add('lorem ipsum hola'.split())  # noqa

    # print(json.dumps(trie.get_data(), indent=4, ensure_ascii=False))

    trie.dump(file_obj, min_freq=0, max_results=100)

    file_obj.seek(0)

    new_trie = Trie.load(file_obj)
    # print(new_trie.data)

    print(json.dumps(new_trie.get_data(), indent=4, ensure_ascii=False))

    print(list(new_trie.fetch([
        ('lorem', 'lorem'),
        ('lorem', 'lorem'),
        ('lorem', 'lorem'),
        ('lorem', 'lorem'),
        ('ipsum', 'ip'),
        ('dolor', 'dolor')
    ], log_enabled=False)))

    # print(list(new_trie.fetch([
    #     ('lorem', 'lorem'),
    # ], log_enabled=False)))
