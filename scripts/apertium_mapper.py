from concurrent.futures import ProcessPoolExecutor
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from src.utils import write_file, print_async
from src.suffixes import ApertiumWrapper


def chunkify(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def process_chunk(words_chunk: list[str], chunk_num: int) -> list[tuple[str, str]]:
    analyzer = ApertiumWrapper()
    results = []

    for i, word in enumerate(words_chunk, 1):
        results.append((word, analyzer.remove_suffix(word)))
        if i % 1000 == 0:
            print_async(f'Processed {i}/{len(words_chunk)} words in chunk {chunk_num}')

    return results


def create_apertium_mapper():
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        words = [line.split(' ')[0] for line in filter(None, file)]
        words_indexed = {word: i for i, word in enumerate(words)}

    num_workers = 4
    chunks = chunkify(words, num_workers)

    print(f'Processing {len(words)} words in {num_workers} parallel chunks...')

    results: list[tuple[str, str]] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_chunk, chunk, chunk_num) for chunk_num, chunk in enumerate(chunks, 1)
        ]

        for i, future in enumerate(futures, 1):
            chunk_result = future.result()
            results.extend(chunk_result)
            print_async(f'Processed chunk {i}/{num_workers} ({len(chunk_result)} words)')

    results.sort(key=lambda x: words_indexed[x[0]])

    write_file(
        mkpath('../results/apertium_mapper.txt'),
        '\n'.join(f'{word} {base}' for word, base in results)
    )


if __name__ == '__main__':
    create_apertium_mapper()
