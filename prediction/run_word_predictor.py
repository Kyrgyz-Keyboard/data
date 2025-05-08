import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie


def main(request: str):
    print('Reading trie...')

    trie = Trie.load_file(mkpath('../results/trie.bin'))
    print(f'Trie knows about {len(trie.words_indexed):,d} words')

    words = list(map(str.lower, request.split()))
    print('Request:', words)

    # print(trie.get_data())

    # if 'covid (False)' in trie.get_data():
    #     print(trie.get_data()['covid (False)'])
    # if 'covid (True)' in trie.get_data():
    #     print(trie.get_data()['covid (True)'])

    # if '19 (False)' in trie.get_data():
    #     print(trie.get_data()['19 (False)'])
    # if '19 (True)' in trie.get_data():
    #     print(trie.get_data()['19 (True)'])
    # print()

    for start_index in range(len(words)):
        print(words[start_index:], list(trie.fetch(words[start_index:])))


if __name__ == '__main__':
    # trie = Trie()
    # trie.add('Сүйүктүү мырзаңызга кандай'.split())
    # with open(mkpath('../results/trie.bin'), 'wb') as file_obj:
    #     trie.dump(file_obj)

    # main('Сүйүктүү мырзаңызга кандай')
    # main('Апам кадрды')
    # main('үйдө компьютер')
    # main('Мен бүгүн дүкөнгө')
    main('COVID 19')
    # main('жаңылыктар')
