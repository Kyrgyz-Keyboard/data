from multiprocessing import Pool, cpu_count
from collections import defaultdict

from datasets import load_dataset

from src.constants import TRANSLATION_TABLE, WORD_PATTERN, INNER_CLEAN_PATTERN, remove_suffixes


def process_chunk(texts: list[str], proc_id: int) -> dict[str, int]:
    word_freq = defaultdict(int)

    log_step = max(1, len(texts) // 10)  # Логируем примерно каждые 10%

    for i, text in enumerate(texts):
        if i % log_step == 0:
            print(f'Process {proc_id}: {i}/{len(texts)}')

        cleaned_text = INNER_CLEAN_PATTERN.sub('', text.lower().translate(TRANSLATION_TABLE))

        for match in WORD_PATTERN.finditer(cleaned_text):
            word_freq[remove_suffixes(match.group())] += 1

    return word_freq


def merge_dicts(dicts: list[dict[str, int]]) -> dict[str, int]:
    final_freq = defaultdict(int)
    for d in dicts:
        for word, count in d.items():
            final_freq[word] += count

    for word, freq in list(final_freq.items()):
        if freq < 100 or len(word) < 2:
            del final_freq[word]

    return final_freq


def main():
    print('Loading dictionary...')
    dictionary = []
    with open('results/all_words_from_dictionary_by_base.txt', 'r', encoding='utf-8') as file:
        for line in filter(None, map(str.strip, file)):
            if not line.startswith('├╴'):
                dictionary.append((line, []))
            else:
                dictionary[-1][1].append(line.removeprefix('├╴'))

    print(f'Dictionary size: {len(dictionary)}')

    word_to_base = {}
    for word, forms in dictionary:
        word_to_base[word] = word
        for form in forms:
            # if form in word_to_base:
            #     print(form)
            word_to_base[form] = word

    print(f'Total word forms: {len(word_to_base)}')

    print('Loading dataset...')
    dataset = load_dataset(
        "HuggingFaceFW/fineweb-2",
        name="kir_Cyrl",
        split="train",
        # streaming=True  # Use streaming to handle large dataset
    )

    size = len(dataset)

    print(f'Total amount of texts: {size}')

    # with open('results/all_texts.txt', 'w', encoding='utf-8') as file:
    #     for i, text in enumerate(dataset['text']):
    #         if i % 100_000 == 0:
    #             print(f'{i}/{len(dataset)}')
    #         file.write(text + '\n---\n')

    print('Loading data to memory...')

    # texts = dataset[:100_000]['text']

    num_workers = cpu_count()
    # num_workers = 1
    chunk_size = size // num_workers
    chunks = [
        (
            dataset[proc_id * chunk_size:(proc_id + 1) * chunk_size]['text'],
            proc_id
        )
        for proc_id in range(num_workers)
    ]

    print(f'Using {num_workers} workers ({cpu_count()} CPUs available) with chunk size: {chunk_size} texts')

    print(f'Processing texts...')
    with Pool(num_workers) as pool:
        results = pool.starmap(process_chunk, chunks)

    print('Merging results...')
    word_freq = merge_dicts(results)
    words_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    print('Saving results...')
    with open('results/word_freq.txt', 'w', encoding='utf-8') as file:
        for word, freq in words_sorted:
            file.write(f'{word} {freq}\n')


if __name__ == "__main__":
    main()
