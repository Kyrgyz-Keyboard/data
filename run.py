from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from time import perf_counter
from math import ceil
import os

from datasets import load_dataset

from src.utils import print_async, FileWriter, empty_file
from src.suffixes import ApertiumMapper, get_appertium_mapper
from src.tokenizer import Tokenizer


BATCH_SIZE = 1_000_000
# os.environ['HF_HUB_OFFLINE'] = '1'


def process_chunk(
    batch_num: int,
    worker_num: int,
    texts: tuple[tuple[int, str], ...],
    apertium_mapper: ApertiumMapper
):
    print_async(f'Worker {batch_num}_{worker_num} started processing {len(texts)} texts')

    sentences: list[list[str]] = []
    sentences_of_bases_apertium: list[list[str]] = []

    word_freq: dict[str, int] = defaultdict(int)
    base_freq_apertium: dict[str, int] = defaultdict(int)

    for _, text in texts:
        # FileWriter.write_file(f'results/texts/{batch_num}_{worker_num}_{text_index}.txt', text)

        for sentence in Tokenizer.process_text(text):
            sentence_of_bases_apertium = []

            for word in sentence:
                # Word may not be in the mapper, if the mapper is outdated
                base_apertium = apertium_mapper.get(word, word)

                word_freq[word] += 1
                base_freq_apertium[base_apertium] += 1

                sentence_of_bases_apertium.append(base_apertium)

            if len(sentence) > 1:
                sentences.append(sentence)
                sentences_of_bases_apertium.append(sentence_of_bases_apertium)

    # print_async(f'Worker {batch_num}_{worker_num} is storing sentences...')
    FileWriter.write_file(
        f'results/sentences/{batch_num}_{worker_num}.txt',
        ''.join(sentence + '\n' for sentence in map(' '.join, sentences))
    )
    FileWriter.write_file(
        'results/sentences.txt',
        ''.join(sentence + '\n' for sentence in map(' '.join, sentences)),
        append=True
    )

    FileWriter.write_file(
        f'results/sentences_of_bases_apertium/{batch_num}_{worker_num}.txt',
        '\n'.join(map(' '.join, sentences_of_bases_apertium)),
    )
    FileWriter.write_file(
        'results/sentences_of_bases_apertium.txt',
        '\n'.join(map(' '.join, sentences_of_bases_apertium)),
        append=True
    )

    # print_async(f'Worker {batch_num}_{worker_num} finished writing results')
    return word_freq, base_freq_apertium


def main():
    bind_args = FileWriter.init()
    apertium_mapper = get_appertium_mapper()

    empty_file('results/sentences.txt')
    empty_file('results/sentences_of_bases_apertium.txt')

    print('Loading dataset...')
    dataset = load_dataset(
        'HuggingFaceFW/fineweb-2',
        name='kir_Cyrl',
        split='train',
        num_proc=4,
        # streaming=True
    ).select_columns('text')

    print(f'Texts in dataset: {len(dataset)}')

    num_workers = os.cpu_count() or 4
    # num_workers = os.process_cpu_count() or os.cpu_count() or 4
    # num_workers = 1
    batches_to_process = ceil(len(dataset) / BATCH_SIZE)
    print(
        f'Using {num_workers} workers and {batches_to_process} batches of size {BATCH_SIZE} '
        f'({max(1, ceil(BATCH_SIZE / num_workers))} texts per run)'
    )

    word_freq: dict[str, int] = defaultdict(int)
    base_apertium_freq: dict[str, int] = defaultdict(int)

    with ProcessPoolExecutor(
        max_workers=num_workers,
        initializer=FileWriter.bind_worker,
        initargs=bind_args
    ) as executor:
        for batch_num, texts in enumerate((batch['text'] for batch in dataset.iter(batch_size=BATCH_SIZE)), 1):
            print_async(f'Processing batch {batch_num}/{batches_to_process}...')
            chunk_size = ceil(len(texts) / num_workers)

            start_time = perf_counter()
            futures = [
                executor.submit(
                    process_chunk,
                    batch_num,
                    i,
                    tuple(
                        ((batch_num - 1) * BATCH_SIZE + (i * chunk_size) + j, text)
                        for j, text in enumerate(texts[i * chunk_size:(i + 1) * chunk_size])
                    ),
                    apertium_mapper
                )
                for i in range(num_workers)
            ]
            del texts

            for future in as_completed(futures):
                # print(f'Merging results from one of the workers in {batch_num}...')
                word_freq_chunk, base_apertium_freq_chunk = future.result()

                for word, freq in word_freq_chunk.items():
                    word_freq[word] += freq
                for base, freq in base_apertium_freq_chunk.items():
                    base_apertium_freq[base] += freq
                del word_freq_chunk, base_apertium_freq_chunk

            print_async(f'Batch processed in {perf_counter() - start_time:.2f} seconds')

    print('Sorting...')
    word_freq_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    base_apertium_freq_sorted = sorted(base_apertium_freq.items(), key=lambda x: x[1], reverse=True)
    del word_freq, base_apertium_freq

    print('Saving results...')
    FileWriter.write_file('results/word_freq.txt', '\n'.join(f'{word} {freq}' for word, freq in word_freq_sorted))
    FileWriter.write_file(
        'results/base_apertium_freq.txt',
        '\n'.join(f'{base} {freq}' for base, freq in base_apertium_freq_sorted)
    )

    FileWriter.stop()


if __name__ == '__main__':
    main()
