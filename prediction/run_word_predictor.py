import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from prediction.trie import Trie, TrieNode


def main(request: str):
    trie = Trie().load_file(mkpath('../results/trie.bin'))
    words = request.split()

    print('Request:', words)
    print(f'Trie knows about {len(trie.words_indexed):,d} words')

    print(len(trie.children))

    cur_obj: TrieNode = trie
    for word in words:
        if trie.words_indexed[word] not in cur_obj.children:
            print(f'Word "{word}" not found as a step')
            return
        cur_obj = cur_obj.children[trie.words_indexed[word]]


if __name__ == '__main__':
    main('Мен сени жакшы')
