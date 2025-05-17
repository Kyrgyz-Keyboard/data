import sys

# import apertium

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie


# analyzer = apertium.Analyzer('kir')


# def get_stem(word: str) -> str | None:
#     bases = []
#     for reading in analyzer.analyze(word)[0].readings:
#         cur_base = reading[0].baseform.replace(' ', '')
#         if '/' not in cur_base and '\\' not in cur_base and cur_base[0] != '*':
#             bases.append(cur_base)

#     if bases:
#         return min(bases, key=lambda s: (len(s), s))
#     return None


def main(request: str):
    print('Reading trie...')

    trie = Trie.load_file(mkpath('../results/trie.bin'))
    print(f'Trie knows about {len(trie.words_indexed):,d} words')

    words = list(map(str.lower, request.split()))
    words_with_stem = [(word, word or word) for word in words]
    print('Request:', words_with_stem)

    # print(len(trie.data))
    # print([word for word in trie.words_indexed.keys() if word.startswith('ме')])
    # print((True, trie.word2index('covid')) in trie.data)
    # print((False, trie.word2index('covid')) in trie.data)
    # print(trie.get_data(trie.data[(False, trie.word2index('covid'))][1]))

    # if 'covid (False)' in trie.get_data():
    #     print(trie.get_data()['covid (False)'])
    # if 'covid (True)' in trie.get_data():
    #     print(trie.get_data()['covid (True)'])

    # if '19 (False)' in trie.get_data():
    #     print(trie.get_data()['19 (False)'])
    # if '19 (True)' in trie.get_data():
    #     print(trie.get_data()['19 (True)'])
    # print()

    # print(list(map(lambda item: trie.words_indexed_reverse[item[1]], trie.data.keys())))
    # print(trie.get_data(
    #     trie.data[(False, trie.word2index('covid'))][1]
    # ))

    # print(trie.get_data(trie.data[(True, trie.word2index('компьютер'))][1]))

    print(words_with_stem, list(trie.fetch(words_with_stem, log_enabled=True)))


if __name__ == '__main__':
    # trie = Trie()
    # trie.add('Сүйүктүү мырзаңызга кандай'.split())
    # with open(mkpath('../results/trie.bin'), 'wb') as file_obj:
    #     trie.dump(file_obj)

    # main('Сүйүктүү мырзаңызга кандай')
    # main('Апам кадрды')
    main('үйдө компьютер')
    # main('Мен бүгүн дүкөнгө')
    # main('COVID 19')
    # main('жаңылыктар')
    # main('Президент өзүнүн бийлигин уламдан улам бекитип')
