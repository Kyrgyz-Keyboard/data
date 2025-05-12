from collections import defaultdict
from collections import deque
from time import perf_counter
import math
import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie


# FINISH_AT_N_BYTES = 1024 * 1024 * 1024  # 1 GB
# FINISH_AT_N_BYTES = 500 * 1024 * 1024  # 500 MB
# FINISH_AT_N_BYTES = 300 * 1024 * 1024  # 300 MB
FINISH_AT_N_BYTES = 100 * 1024 * 1024  # 100 MB
# FINISH_AT_N_BYTES = 30 * 1024 * 1024  # 30 MB
# FINISH_AT_N_BYTES = 10 * 1024 * 1024  # 10 MB
# FINISH_AT_N_BYTES = 1024  # 1 KB

LOG_EVERY_N_BYTES = 10 * 1024 * 1024  # 10 MB


WORD_FREQ_THRESHOLD = 10
RESULT_FREQ_THRESHOLD = 3


def size_to_str(size_bytes: int) -> str:
    if size_bytes == 0:
        return '0 B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s} {size_name[i]}'


def build_trie():
    print('Reading words list...')
    word_size = {}
    word_freq: dict[str, int] = defaultdict(int)
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        for line in map(str.strip, filter(None, file)):
            word, freq = line.split()
            word = word.lower()
            word_freq[word] += int(freq)
            word_size[word] = len(word.encode('utf-8'))

    allowed_words: set[str] = {
        word
        for word, freq in word_freq.items()
        if freq >= WORD_FREQ_THRESHOLD
    }
    del word_freq

    print(f'Allowed words: {len(allowed_words):,d}')

    print('Reading Apertium mapper...')
    apertium_mapper: dict[str, str] = {}
    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        for line in map(str.strip, filter(None, file)):
            if ' ' in line:
                key, value = map(str.lower, line.split(' '))
                apertium_mapper[key] = value

    print(f'Apertium Mapper: {len(apertium_mapper):,d} -> {len(set(apertium_mapper.values())):,d}')

    print('Preparation done')
    print()

    source_file_size = os.path.getsize(mkpath('../results/sentences.txt'))
    print(f'Source file size: {size_to_str(source_file_size)}')

    print('Building trie...')
    trie = Trie(allowed_words, apertium_mapper)

    total_read_size = 0
    next_log = LOG_EVERY_N_BYTES
    start_time = perf_counter()

    with open(mkpath('../results/sentences.txt'), 'r', encoding='utf-8') as file:
        for sentence in map(str.strip, file):
            word_window: deque[str] = deque(maxlen=Trie.MAX_LAYERS)

            for word in map(str.lower, sentence.split(' ')):
                total_read_size += word_size[word]

                word_window.append(word)
                trie.add(word_window)

            if total_read_size >= next_log:
                print(
                    f'Processed {size_to_str(total_read_size)} / {size_to_str(source_file_size)} bytes in '
                    f'{perf_counter() - start_time:.0f} seconds'
                )
                next_log += LOG_EVERY_N_BYTES

            # if total_read_size >= FINISH_AT_N_BYTES:
            #     break

    print('Writing trie to file...')
    trie.dump_file(mkpath('../results/trie.bin'), RESULT_FREQ_THRESHOLD)

    trie_size = os.path.getsize(mkpath('../results/trie.bin'))
    print(f'Trie size: {size_to_str(trie_size)}')


if __name__ == '__main__':
    trie = build_trie()
