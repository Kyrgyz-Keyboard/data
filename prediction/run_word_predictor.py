import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie


def main(request: str):
    trie = Trie().load_file(mkpath('../results/trie.bin'))
    words = request.split()

    print('Request:', words)
    print(f'Trie knows about {len(trie.words_indexed):,d} words')

    print(len(trie.children))
    print(trie.children[trie.words_indexed['Мен']])

    print(trie.fetch(words))


if __name__ == '__main__':
    main('Мен сени жакшы')
