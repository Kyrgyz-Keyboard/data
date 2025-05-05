import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


def count_words(min_freq=0):
    print(f'--- Freq >= {min_freq} ---')

    letters: set[str] = set()
    words, apertium_words = set(), set()

    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        for line in filter(None, file):
            word, freq = line.split(' ')
            if int(freq) < min_freq:
                continue
            words.add(word)
            letters.update(word)

    print(f'Words:          {len(words):{9 + 2},d}')

    with open(mkpath('../results/base_apertium_freq.txt'), 'r', encoding='utf-8') as file:
        for line in filter(None, file):
            word, freq = line.split(' ')
            if int(freq) < min_freq:
                continue
            apertium_words.add(word)
            letters.update(word)

    print(f'Apertium words: {len(apertium_words):{9 + 2},d} ({len(apertium_words) / len(words):.2%})')
    print()

    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        mapper_keys, mapper_values, mapper_unmapped = set(), set(), set()
        for line in map(str.strip, filter(None, file)):
            if ' ' in line:
                key, value = line.split(' ')
                if key not in words:
                    continue
                mapper_keys.add(key)
                mapper_values.add(value)
            else:
                if line not in words:
                    continue
                mapper_unmapped.add(line)

    print(
        f'{len(mapper_keys):,d} words mapped to {len(mapper_values):,d} apertium base words '
        f'(reduction: {len(mapper_values) / len(mapper_keys):.2%})'
    )
    print(
        f'{len(mapper_unmapped):,d} words '
        f'({len(mapper_unmapped) / (len(mapper_unmapped) + len(mapper_keys)):.2%}) '
        f'are mapped to nothing'
    )
    print(
        f'Total reduction: '
        f'{(len(mapper_unmapped) + len(mapper_values)) / (len(mapper_unmapped) + len(mapper_keys)):.2%}'
    )

    print()
    print('Distinct letters:', len(letters))
    print(''.join(sorted(letters)))


if __name__ == '__main__':
    count_words()
    print()
    print()
    count_words(min_freq=100)
