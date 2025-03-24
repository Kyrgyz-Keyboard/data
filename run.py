from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock as LockType
from multiprocessing import Manager
from time import perf_counter
from math import ceil
import os

from datasets import load_dataset

from src.suffixes import SuffixTrie, get_suffix_trie
from src.tokenizer import Tokenizer


BATCH_SIZE = 100_000
# os.environ['HF_HUB_OFFLINE'] = '1'

tokenizer = Tokenizer()


def process_chunk(
    batch_num: int,
    worker_num: int,
    file_sys_lock: LockType,
    texts: tuple[tuple[int, str], ...],
    suffix_trie: SuffixTrie,
):
    # print(f'Worker {batch_num}_{worker_num} started processing {len(texts)} texts')

    sentencies: list[list[str]] = []
    sentencies_of_bases: list[list[str]] = []
    sentencies_of_suffixes: list[list[str]] = []

    word_freq: dict[str, int] = {}
    base_freq: dict[str, int] = {}
    suffix_freq: dict[str, int] = {}

    for _, text in texts:
        # with open(f'results/texts/{text_id}.txt', 'w', encoding='utf-8') as file:
        #     file.write(text)

        for sentence in tokenizer.process_text(text):
            sentencies.append([])
            sentencies_of_bases.append([])
            sentencies_of_suffixes.append([])
            for word in sentence:
                word_freq[word] += 1
                base, suffix = suffix_trie.remove_suffix(word)
                base_freq[base] += 1
                suffix_freq[suffix] += 1

                sentencies[-1].append(word)
                sentencies_of_bases[-1].append(base)
                sentencies_of_suffixes[-1].append(suffix)

    with open(f'results/sentencies/{batch_num}_{worker_num}.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies)))
    with file_sys_lock, open('results/sentencies.txt', 'a', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies)))

    with open(f'results/sentencies_of_bases/{batch_num}_{worker_num}.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies_of_bases)))
    with file_sys_lock, open('results/sentencies_of_bases.txt', 'a', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies_of_bases)))

    with open(f'results/sentencies_of_suffixes/{batch_num}_{worker_num}.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies_of_suffixes)))
    with file_sys_lock, open('results/sentencies_of_suffixes.txt', 'a', encoding='utf-8') as file:
        file.write('\n'.join(map(' '.join, sentencies_of_suffixes)))

    return word_freq, base_freq, suffix_freq


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

    word_freq: dict[str, int] = {}
    base_freq: dict[str, int] = {}
    suffix_freq: dict[str, int] = {}

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
                word_freq_chunk, base_freq_chunk, suffix_freq_chunk = future.result()
                word_freq = {
                    word: word_freq.get(word, 0) + freq
                    for word, freq in word_freq_chunk.items()
                }
                base_freq = {
                    base: base_freq.get(base, 0) + freq
                    for base, freq in base_freq_chunk.items()
                }
                suffix_freq = {
                    suffix: suffix_freq.get(suffix, 0) + freq
                    for suffix, freq in suffix_freq_chunk.items()
                }
                del word_freq_chunk, base_freq_chunk, suffix_freq_chunk

        print(f'Batch processed in {perf_counter() - start_time:.2f} seconds')
        del chunks

    print('Cleaning results...')
    # word_freq = {word: freq for word, freq in word_freq.items() if freq >= 100 and len(word) > 1}
    word_freq = {word: freq for word, freq in word_freq.items() if len(word) > 1}

    print('Sorting...')
    word_freq_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    base_freq_sorted = sorted(base_freq.items(), key=lambda x: x[1], reverse=True)
    suffix_freq_sorted = sorted(suffix_freq.items(), key=lambda x: x[1], reverse=True)
    del word_freq, base_freq, suffix_freq

    print('Saving results...')
    with open('results/word_freq.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(f'{word} {freq}' for word, freq in word_freq_sorted))
    with open('results/base_freq.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(f'{base} {freq}' for base, freq in base_freq_sorted))
    with open('results/suffix_freq.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(f'{suffix} {freq}' for suffix, freq in suffix_freq_sorted))


if __name__ == '__main__':
    main()
