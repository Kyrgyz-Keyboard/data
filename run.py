from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock as LockType
from multiprocessing import Manager
# from collections import defaultdict
from time import perf_counter
from math import ceil
import os

from datasets import load_dataset

# from src.constants import TRANSLATION_TABLE, WORD_PATTERN  # , INNER_CLEAN_PATTERN
from src.suffixes import SuffixTrie, get_suffix_trie
from src.tokenizer import Tokenizer


BATCH_SIZE = 100_000
# os.environ['HF_HUB_OFFLINE'] = '1'

tokenizer = Tokenizer()


def process_chunk(
    batch_num: int,
    worker_num: int,
    file_sys_lock: LockType,
    texts: list[tuple[int, str]],
    suffix_trie: SuffixTrie,
):
    # print(f'Worker {batch_num}_{worker_num} started processing {len(texts)} texts')
    # sentencies: list[str] = []
    word_bases: set[str] = set()

    for text_id, text in texts:
        # with open(f'results/texts/{text_id}.txt', 'w', encoding='utf-8') as file:
        #     file.write(text)

        # sentencies.extend(map(' '.join, tokenizer.process_text(text)))

        # for match in WORD_PATTERN.finditer(text.lower().translate(TRANSLATION_TABLE)):
        #     word_freq[suffix_trie.remove_suffixes(match.group())] += 1

        for sentence in tokenizer.process_text(text):
            for word in sentence:
                word_bases.add(suffix_trie.remove_suffixes(word))

    # with open(f'results/sentencies/{batch_num}_{worker_num}.txt', 'w', encoding='utf-8') as file:
    #     file.write('\n'.join(sentencies))

    # with file_sys_lock, open('results/sentencies.txt', 'a', encoding='utf-8') as file:
    #     file.write('\n'.join(sentencies))

    # return sentencies
    return word_bases


# def merge_dicts(*dicts: dict[str, int]) -> dict[str, int]:
#     result: dict[str, int] = defaultdict(int)
#     for d in dicts:
#         for word, count in d.items():
#             result[word] += count
#     return result


def main():
    suffix_trie = get_suffix_trie()
    file_sys_lock = Manager().Lock()

    with open('results/sentencies.txt', 'w', encoding='utf-8'):
        pass

    print('Loading dataset...')
    dataset = load_dataset(
        'HuggingFaceFW/fineweb-2',
        name='kir_Cyrl',
        split='train',
        num_proc=4,
        # streaming=True
    )

    print(f'Texts in dataset: {len(dataset)}')

    num_workers = os.process_cpu_count() or os.cpu_count() or 4
    # num_workers = 1
    batches_to_process = ceil(len(dataset) / BATCH_SIZE)
    print(
        f'Using {num_workers} workers and {batches_to_process} batches of size {BATCH_SIZE} '
        f'({max(1, ceil(BATCH_SIZE / num_workers))} texts per run)'
    )

    # word_freq: dict[str, int] = defaultdict(int)
    # sentencies: list[str] = []
    all_word_bases: set[str] = set()

    for batch_num, batch in enumerate(dataset.iter(batch_size=BATCH_SIZE), 1):
        print(f'Processing batch {batch_num}/{batches_to_process}...')
        texts = batch['text']
        del batch

        chunk_size = max(1, ceil(len(texts) / num_workers))
        chunks = tuple(
            tuple(
                (i, text)
                for text in texts[i:i + chunk_size]
            )
            for i in range(0, len(texts), chunk_size)
        )
        del texts

        start_time = perf_counter()

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # print('Running workers...')
            for future in as_completed((
                executor.submit(
                    process_chunk,
                    batch_num,
                    i,
                    file_sys_lock,
                    chunk,
                    suffix_trie
                )
                for i, chunk in enumerate(chunks)
            )):
                # sentencies.extend(future.result())
                all_word_bases.update(future.result())

        print(f'Batch processed in {perf_counter() - start_time:.2f} seconds')
        del chunks

        # print('Merging partial results...')
        # word_freq = merge_dicts(word_freq, *results)
        # for result in results:
        #     sentencies.extend(result)

    print('Cleaning results...')
    # word_freq = {
    #     word: freq
    #     for word, freq in word_freq.items()
    #     if freq >= 100 and len(word) >= 2
    # }
    all_word_bases = {
        word
        for word in all_word_bases
        if len(word) >= 2
    }

    # print('Sorting...')
    # words_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    # del word_freq
    all_word_bases_sorted = sorted(all_word_bases)
    del all_word_bases

    print('Saving results...')
    # with open('results/word_freq.txt', 'w', encoding='utf-8') as file:
    #     file.write('\n'.join(f'{word} {freq}' for word, freq in words_sorted))
    # with open('results/sentencies.txt', 'w', encoding='utf-8') as file:
    #     file.write('\n'.join(sentencies))
    with open('results/word_bases.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(all_word_bases_sorted))


if __name__ == '__main__':
    main()
