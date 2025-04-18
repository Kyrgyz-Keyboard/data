import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


def count_words():
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        print('Words:\t\t\t\t', sum(1 for _ in filter(None, file)))

    with open(mkpath('../results/base_simple_freq.txt'), 'r', encoding='utf-8') as file:
        print('Base simple words:\t', sum(1 for _ in filter(None, file)))

    with open(mkpath('../results/apertium_mapper.txt'), 'r', encoding='utf-8') as file:
        apertium_mapper = [list(map(str.strip, line.split(' ', 1))) for line in filter(None, file)]
        apertium_mapper_reverse = {apertium_base for _, apertium_base in apertium_mapper}
        print(len(apertium_mapper), 'words mapped to', len(apertium_mapper_reverse), 'apertium base words')


if __name__ == '__main__':
    count_words()
