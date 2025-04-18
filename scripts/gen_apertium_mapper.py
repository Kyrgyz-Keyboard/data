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


def process_chunk(words_chunk: list[str], chunk_num: int) -> list[list[str]]:
    analyzer = apertium.Analyzer('kir')

    results = []

    for i, word in enumerate(words_chunk, 1):
        base = min(
            reading[0].baseform.lstrip('*')
            for reading in analyzer.analyze(word)[0].readings
        )
        results.append([word, base])

        if i % 1000 == 0:
            print_async(f'Processed {i}/{len(words_chunk)} words in chunk {chunk_num}')

    return results


def create_apertium_mapper():
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        words = [line.split(' ')[0].strip() for line in filter(None, file)]
        words_indexed = {word: i for i, word in enumerate(words)}

    num_workers = 4
    chunks = chunkify(words, num_workers)

    print(f'Processing {len(words)} words in {num_workers} parallel chunks...')

    results: list[list[str]] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for i, future in enumerate(as_completed(
            executor.submit(process_chunk, chunk, chunk_num) for chunk_num, chunk in enumerate(chunks, 1)
        ), 1):
            chunk_result = future.result()
            results.extend(chunk_result)
            print(f'Processed chunk {i} ({len(chunk_result)} words)')

    results.sort(key=lambda x: words_indexed[x[0]])

    # Fix the base for 'жана' to be 'жана'
    for item in results:
        if item[0].lower() == 'жана':
            item[1] = item[0]

    write_file(
        mkpath('../results/apertium_mapper.txt'),
        '\n'.join(f'{word} {base}' for word, base in results)
    )


if __name__ == '__main__':
    apertium_analyzer = apertium.Analyzer('kir')

    print(apertium_analyzer.analyze('эларалык'))
