import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie


def main(request: str):
    trie = Trie().load_file(mkpath('../results/trie.bin'))
    words = list(map(str.lower, request.split()))

    print('Request:', words)
    print(f'Trie knows about {len(trie.words_indexed):,d} words')

    print(trie.fetch(['Сүйүктүү'.lower()]))
    print()

    for start_index in range(len(words)):
        print(words[start_index:], trie.fetch(words[start_index:]))


if __name__ == '__main__':
    # trie = Trie()
    # trie.add('Сүйүктүү мырзаңызга кандай'.split())
    # with open(mkpath('../results/trie.bin'), 'wb') as file_obj:
    #     trie.dump(file_obj)

    main('Сүйүктүү мырзаңызга кандай')
    # main('Апам кадрды')
    # main('COVID 19')
