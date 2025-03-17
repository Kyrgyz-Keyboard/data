from multiprocessing import Pool, cpu_count
from collections import defaultdict
from math import ceil

from datasets import load_dataset

from src.constants import TRANSLATION_TABLE, WORD_PATTERN, INNER_CLEAN_PATTERN
from src.suffixes import SuffixTrie, get_suffix_trie, remove_suffixes


BATCH_SIZE = 250_000


def process_chunk(worker_id: int, texts: list[str], suffix_trie: SuffixTrie) -> dict[str, int]:
    print(f'Worker {worker_id} started processing {len(texts)} texts...')
    word_freq = defaultdict(int)

    for text in texts:
        cleaned_text = INNER_CLEAN_PATTERN.sub('', text.lower().translate(TRANSLATION_TABLE))

        for match in WORD_PATTERN.finditer(cleaned_text):
            word_freq[remove_suffixes(suffix_trie, match.group())] += 1

    return word_freq


def merge_dicts(*dicts: dict[str, int]) -> dict[str, int]:
    result = defaultdict(int)
    for d in dicts:
        for word, count in d.items():
            result[word] += count

    return result


def main():
    suffix_trie = get_suffix_trie()

    print('Loading dataset...')
    dataset = load_dataset(
        "HuggingFaceFW/fineweb-2",
        name="kir_Cyrl",
        split="train",
        # streaming=True
    )

    print(f'Texts in dataset: {len(dataset)}')

    num_workers = cpu_count()
    # num_workers = 1
    print(
        f'Using {num_workers} workers and batches of size {BATCH_SIZE} '
        f'({max(1, ceil(BATCH_SIZE / num_workers))} texts per worker)'
    )

    word_freq = {}
    batches_to_process = ceil(len(dataset) / BATCH_SIZE)

    for batch_num, batch in enumerate(dataset.iter(batch_size=BATCH_SIZE), 1):
        print(f'Processing batch {batch_num}/{batches_to_process}...')
        texts = batch['text']

        chunk_size = max(1, ceil(len(texts) / num_workers))
        chunks = tuple(tuple(texts[i:i + chunk_size]) for i in range(0, len(texts), chunk_size))

        # print('Running workers...')
        with Pool(num_workers) as pool:
            results = pool.starmap(process_chunk, tuple(
                (worker_id, chunk, suffix_trie) for worker_id, chunk in enumerate(chunks)
            ))

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


if __name__ == "__main__":
    main()
