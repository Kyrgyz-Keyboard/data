from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from time import perf_counter
from itertools import repeat
from math import ceil
import os

from datasets import load_dataset

from src.constants import TRANSLATION_TABLE, WORD_PATTERN  # , INNER_CLEAN_PATTERN
from src.suffixes import SuffixTrie, get_suffix_trie


BATCH_SIZE = 100_000
# os.environ['HF_HUB_OFFLINE'] = '1'


def process_chunk(worker_id: int, texts: list[str], suffix_trie: SuffixTrie) -> dict[str, int]:
    word_freq: dict[str, int] = defaultdict(int)

    for text in texts:
        # cleaned_text = INNER_CLEAN_PATTERN.sub('', text.lower().translate(TRANSLATION_TABLE))
        # cleaned_text = text.lower().translate(TRANSLATION_TABLE)

        for match in WORD_PATTERN.finditer(text.lower().translate(TRANSLATION_TABLE)):
            word_freq[suffix_trie.remove_suffixes(match.group())] += 1
            # word_freq[match.group()] += 1

    return word_freq


def merge_dicts(*dicts: dict[str, int]) -> dict[str, int]:
    result: dict[str, int] = defaultdict(int)
    for d in dicts:
        for word, count in d.items():
            result[word] += count

    return result


def main():
    suffix_trie = get_suffix_trie()

    print('Loading dataset...')
    dataset = load_dataset(
        'HuggingFaceFW/fineweb-2',
        name='kir_Cyrl',
        split='train',
        num_proc=4,
        # streaming=True
    )

    print(f'Texts in dataset: {len(dataset)}')

    num_workers = os.cpu_count()
    # num_workers = 1
    batches_to_process = ceil(len(dataset) / BATCH_SIZE)
    print(
        f'Using {num_workers} workers and {batches_to_process} batches of size {BATCH_SIZE} '
        f'({max(1, ceil(BATCH_SIZE / num_workers))} texts per run)'
    )

    word_freq: dict[str, int] = defaultdict(int)

    for batch_num, batch in enumerate(dataset.iter(batch_size=BATCH_SIZE), 1):
        print(f'Processing batch {batch_num}/{batches_to_process}...')
        texts = batch['text']
        del batch

        chunk_size = max(1, ceil(len(texts) / num_workers))
        chunks = tuple(tuple(texts[i:i + chunk_size]) for i in range(0, len(texts), chunk_size))
        del texts

        start_time = perf_counter()

        # print('Running workers...')
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            results = executor.map(process_chunk, range(len(chunks)), chunks, repeat(suffix_trie, times=len(chunks)))

        print(f'Batch processed in {perf_counter() - start_time:.2f} seconds')
        del chunks

        # print('Merging partial results...')
        word_freq = merge_dicts(word_freq, *results)

    print('Cleaning results...')
    word_freq = {
        word: freq
        for word, freq in word_freq.items()
        if freq >= 100 and len(word) >= 2
    }

    print('Sorting...')
    words_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    print('Saving results...')
    with open('results/word_freq.txt', 'w', encoding='utf-8') as file:
        for word, freq in words_sorted:
            file.write(f'{word} {freq}\n')


if __name__ == '__main__':
    main()
