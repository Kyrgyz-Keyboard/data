import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

# from prediction.trie import Trie


def main(request: str):
    # trie = Trie.load_file(mkpath('../results/trie.json'))
    words = request.split()

    print(words)


if __name__ == '__main__':
    main('Мен сени жакшы')
