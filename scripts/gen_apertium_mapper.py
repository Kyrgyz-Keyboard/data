# Runs only on Linux/MacOS. Use WSL on Windows

# Apertium should be installed separately.
# TODO: create instructions for installation and `requirements.txt`


from typing import Iterable, Generator, TypeVar

from concurrent.futures import ProcessPoolExecutor, as_completed
from math import ceil
import itertools
import sys
import os

import apertium

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic, empty_file
mkpath = PathMagic(__file__)

from src.utils import write_file, print_async


KYRGYZ_WHITELIST_WORDS = {
    # Conjunctions
    'жана', 'же', 'бирок', 'анткени', 'ошондуктан', 'себеби', 'болбосо', 'менен',

    # Prepositions and postpositions
    'үчүн', 'чейин', 'кийин', 'үстүндө', 'ичинде', 'сыртында', 'алдында', 'артында',

    # Particles and introductory words
    'эле', 'да', 'де', 'дагы', 'гана', 'го', 'даана', 'балким', 'эми', 'мурда',

    # Pronouns
    'бул', 'ал', 'мен', 'сен', 'сиз', 'биз', 'силер', 'алар',
}


T = TypeVar('T')


def batched(iterable: Iterable[T], n: int) -> Generator[list[T], None, None]:
    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            break
        yield chunk


def process_chunk(
    words_chunk: list[str] | tuple[str, ...],
    chunk_num: int
) -> list[tuple[str, str | None]]:

    analyzer = apertium.Analyzer('kir')
    results = []

    for i, word in enumerate(words_chunk, 1):
        bases = []
        for reading in analyzer.analyze(word)[0].readings:
            cur_base = reading[0].baseform.replace(' ', '')
            if '/' not in cur_base and '\\' not in cur_base and cur_base[0] != '*':
                bases.append(cur_base)

        results.append((word, min(bases, key=lambda s: (len(s), s)) if bases else None))

        if i % 1000 == 0:
            print_async(f'Processed {i:,d}/{len(words_chunk):,d} words in chunk {chunk_num}')

    return results


def create_apertium_mapper():
    if not os.path.isfile(mkpath('../results/word_freq.txt')):
        print(
            '[Apertium] Word frequency file not found. '
            'Please run the main script (`/run.py`) first.'
        )
        return

    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        words_indexed = {}
        for i, line in enumerate(map(str.strip, filter(None, file))):
            word, freq = line.split(' ')
            # if int(freq) >= 10:
            words_indexed[word] = i

    if not os.path.isfile(mkpath('../results/apertium_mapper.txt')):
        empty_file(mkpath('../results/apertium_mapper.txt'))

    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        apertium_mapper: dict[str, str | None] = {}

        for line in map(str.strip, filter(None, file)):
            if ' ' in line:
                word, base = map(str.strip, line.split(' '))
                apertium_mapper[word] = base
            else:
                apertium_mapper[line.strip()] = None

    old_size = len(apertium_mapper)

    apertium_mapper = {
        word: base
        for word, base in apertium_mapper.items()
        if word in words_indexed
    }

    print(f'Removed {old_size - len(apertium_mapper):,d} words from the mapper')

    to_process = list(set(words_indexed.keys()) - set(apertium_mapper.keys()) - KYRGYZ_WHITELIST_WORDS)

    to_process = to_process[:500_000]

    num_workers = os.cpu_count() or 4
    chunk_size = ceil(len(to_process) / num_workers)

    print(f'Processing {len(to_process):,d} words in {num_workers} parallel chunks...')

    added_count = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for i, future in enumerate(as_completed(
            executor.submit(process_chunk, chunk, chunk_num)
            for chunk_num, chunk in enumerate(batched(to_process, chunk_size or 1), 1)
        ), 1):
            chunk_result = future.result()
            apertium_mapper.update(chunk_result)
            added_count += len(chunk_result)
            print(f'Processed chunk {i} ({len(chunk_result)} words)')

    print(f'Added {added_count:,d} new words to the mapper')

    for word in KYRGYZ_WHITELIST_WORDS:
        if word in words_indexed:
            apertium_mapper[word] = word

    if len(apertium_mapper) != len(words_indexed):
        print(f'Warning: {len(apertium_mapper):,d} instead of {len(words_indexed):,d} words in the mapper')

    write_file(
        mkpath('../results/apertium_mapper.txt'),
        '\n'.join(
            (word if base is None or base == word else f'{word} {base}')
            for word, base in sorted(apertium_mapper.items(), key=lambda x: words_indexed[x[0]])
        )
    )


if __name__ == '__main__':
    # apertium_analyzer = apertium.Analyzer('kir')

    # print(apertium_analyzer.analyze('англисчени'))
    # print(apertium_analyzer.analyze('англисчени')[0].readings)

    create_apertium_mapper()
