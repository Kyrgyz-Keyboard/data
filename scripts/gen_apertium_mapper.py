# Runs only on Linux/MacOS

from typing import TypeVar, Iterator

from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

import apertium

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from src.utils import write_file, print_async


T = TypeVar('T')


def chunkify(array: list[T], n: int) -> Iterator[list[T]]:
    k, m = divmod(len(array), n)
    yield from (
        array[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
        for i in range(n)
    )


def process_chunk(
    words_chunk: list[str],
    chunk_num: int,
    apertium_mapper: dict[str, str | None]
) -> list[tuple[str, str | None]]:

    analyzer = apertium.Analyzer('kir')
    results = []

    for i, word in enumerate(words_chunk, 1):
        if word not in apertium_mapper:
            bases = []
            for reading in analyzer.analyze(word)[0].readings:
                cur_base = reading[0].baseform.replace(' ', '')
                if cur_base[0] != '*':
                    bases.append(cur_base)

            results.append((word, min(bases) if bases else None))

        if i % 1000 == 0:
            print_async(f'Processed {i}/{len(words_chunk)} words in chunk {chunk_num}')

    return results


def create_apertium_mapper():
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        words_indexed = {
            word: i
            for i, word in enumerate(
                line.split(' ', 1)[0].strip()
                for line in filter(None, file)
            )
        }

    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        apertium_mapper: dict[str, str | None] = {}

        for line in map(str.strip, filter(None, file)):
            if ' ' in line:
                word, base = map(str.strip, line.split(' '))
                apertium_mapper[word] = base
            else:
                apertium_mapper[line.strip()] = None

    old_size = len(apertium_mapper)

    for word in list(apertium_mapper):
        if word not in words_indexed:
            del apertium_mapper[word]

    print(f'Removed {old_size - len(apertium_mapper)} words from the mapper')

    to_process = list(set(words_indexed.keys()) - set(apertium_mapper.keys()))

    num_workers = 4
    chunks = chunkify(to_process, num_workers)

    print(f'Processing {len(to_process)} words in {num_workers} parallel chunks...')

    added_count = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for i, future in enumerate(as_completed(
            executor.submit(process_chunk, chunk, chunk_num, apertium_mapper)
            for chunk_num, chunk in enumerate(chunks, 1)
        ), 1):
            chunk_result = future.result()
            for word, base_opt in chunk_result:
                apertium_mapper[word] = base_opt
            added_count += len(chunk_result)
            print(f'Processed chunk {i} ({len(chunk_result)} words)')

    print(f'Added {added_count} new words to the mapper')

    assert len(apertium_mapper) == len(words_indexed)

    apertium_mapper['жана'] = 'жана'

    write_file(
        mkpath('../results/apertium_mapper.txt'),
        '\n'.join(
            (word if base is None else f'{word} {base}')
            for word, base in sorted(apertium_mapper.items(), key=lambda x: words_indexed[x[0]])
        )
    )


if __name__ == '__main__':
    # apertium_analyzer = apertium.Analyzer('kir')

    # print(apertium_analyzer.analyze('эларалык'))

    create_apertium_mapper()
