import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


def count_words():
    letters: set[str] = set()

    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        for word_count, line in enumerate(filter(None, file)):
            word, _ = line.split(' ')
            letters.update(word)
            word_count += 1

        print('Words:\t\t\t', word_count)

    with open(mkpath('../results/base_apertium_freq.txt'), 'r', encoding='utf-8') as file:
        print('Apertium words:\t', sum(1 for _ in filter(None, file)))

    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        apertium_mapper_keys, apertium_mapper_values = set(), set()
        for line in filter(None, file):
            if ' ' in line:
                key, value = line.split(' ')
                apertium_mapper_keys.add(key)
                apertium_mapper_values.add(value)
            else:
                apertium_mapper_keys.add(line)
        print(len(apertium_mapper_keys), 'words mapped to', len(apertium_mapper_values), 'apertium base words')

    print()
    print('Distinct letters:', len(letters))
    print(''.join(sorted(letters)))


if __name__ == '__main__':
    count_words()
