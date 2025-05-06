from collections import deque
from time import perf_counter
import math
import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import LAYERS, Trie


LOG_EVERY_N_BYTES = 100 * 1024 * 1024  # 100 MB
# LOG_EVERY_N_BYTES = 30 * 1024 * 1024  # 30 MB
# LOG_EVERY_N_BYTES = 1024  # 1 KB


def size_to_str(size_bytes: int) -> str:
    if size_bytes == 0:
        return '0 B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s} {size_name[i]}'


def build_trie():
    print('Constructing words list...')
    word_size = {}
    word_freq = {}
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        for line in map(str.strip, filter(None, file)):
            word, freq = line.split()
            word_freq[word] = int(freq)
            word_size[word] = len(word.encode('utf-8'))

    print('Building trie...')

    file_size = os.path.getsize(mkpath('../results/sentences.txt'))
    print(f'File size: {size_to_str(file_size)}')

    trie = Trie()

    total_read_size = 0
    next_log = LOG_EVERY_N_BYTES
    start_time = perf_counter()

    with open(mkpath('../results/sentences.txt'), 'r', encoding='utf-8') as file:
        for sentence in map(str.strip, file):
            word_window: deque[str] = deque(maxlen=len(LAYERS))

            # if len(sentence.split(' ')) < 10:
            #     continue

            for word in sentence.split(' '):
                # assert word_size[word], 'Empty word found'
                total_read_size += word_size[word]

                if word_freq[word] < 100:
                    word_window.clear()
                    continue

                word_window.append(word)

                if word_window:
                    # print('Adding', word_window)
                    trie.add(word_window)

            if total_read_size >= next_log:
                print(
                    f'Processed {size_to_str(total_read_size)} / {size_to_str(file_size)} bytes in '
                    f'{perf_counter() - start_time:.0f} seconds'
                )
                next_log += LOG_EVERY_N_BYTES

                break

    trie.dump_file(mkpath('../results/trie.bin'))


if __name__ == '__main__':
    trie = build_trie()
