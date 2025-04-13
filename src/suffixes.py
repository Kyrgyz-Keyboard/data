from functools import cache
import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.get_dictionary import get_kaikki_tili, get_kyrgyz_tili
from src.tokenizer import Tokenizer
from src.utils import write_file


file_location = os.path.dirname(os.path.abspath(__file__))


class SuffixTrie:
    TrieInner = dict[str, 'TrieInner']

    def __init__(self, suffixes: set[str]):
        self.trie: SuffixTrie.TrieInner = {}
        for suffix in suffixes:
            node: SuffixTrie.TrieInner = self.trie
            for char in reversed(suffix):
                node = node.setdefault(char, {})
            node['$'] = {}

    @cache  # noqa
    def remove_suffix(self, word: str) -> tuple[str, str]:
        node = self.trie
        longest_index = len(word)

        for i in range(len(word) - 1, -1, -1):
            char = word[i]
            if char not in node:
                break
            node = node[char]
            if '$' in node:
                longest_index = i

        return word[:longest_index], word[longest_index:]


def get_suffix_trie() -> SuffixTrie:
    dictionary, _ = get_kaikki_tili()
    kyrgyz_tili_dictionary, _ = get_kyrgyz_tili()

    handmade_suffixes = {
        'чы', 'чи', 'чу', 'чү',
        'ба', 'бе', 'бо', 'бө',

        'мын', 'мин', 'мун', 'мүн',
        'сың', 'сиң', 'суң', 'сүң',
        'сыз', 'сиз', 'суз', 'сүз',
        'быз', 'биз', 'буз', 'бүз',
        'пыз', 'пиз', 'пуз', 'пүз',

        'сыңар', 'сиңер', 'суңар', 'сүңөр',
        'сыздар', 'сиздер', 'суздар', 'сүздөр',

        'нын', 'нин', 'нун', 'нүн',
        'дын', 'дин', 'дун', 'дүн',
        'тын', 'тин', 'тун', 'түн',

        'га', 'ге', 'го', 'гө',

        'дар', 'дер', 'дор', 'дөр',
        'тар', 'тер', 'тор', 'төр',
        'лар', 'лер', 'лор', 'лөр',

        'па', 'пе', 'по', 'пө',
        'би', 'бу', 'бү', 'бы',
        'пи', 'пу', 'пү', 'пы',

        'тон', 'төн', 'тан', 'тен',
        'дон', 'дөн', 'дан', 'ден',

        'ги', 'гу', 'гы', 'гү',
        'ки', 'ку', 'кы', 'кү',
        'ка', 'ке', 'ко', 'кө',

        'гун', 'гүн', 'гын', 'гин',
        'кун', 'күн', 'кын', 'кин',

        'даш', 'деш', 'дош', 'дөш',
        'таш', 'теш', 'тош', 'төш',

        'йм', 'өм', 'ам', 'ем', 'ом',

        'да', 'де', 'до', 'дө',
        'та', 'те', 'то', 'тө',
        'ына',

        'лик', 'лак', 'лөк', 'лок', 'лук', 'лүк',

        'ум', 'үм'
    }
    suffixes = {suffix.translate(Tokenizer.TRANSLATION_TABLE) for suffix in handmade_suffixes}

    print(f'[Suffixes] Hand-made suffixes: {len(suffixes)}')

    dictionary_suffixes = set()
    for word, forms in dictionary.items():
        for form in forms:
            if not form.startswith(word):
                continue
            suffix = form.removeprefix(word)
            if suffix:
                dictionary_suffixes.add(suffix)

    print(f'[Suffixes] Dictionary suffixes: {len(dictionary_suffixes)}')

    kyrgyz_tili_dictionary_suffixes = set()
    for word, forms in kyrgyz_tili_dictionary.items():
        for form in forms:
            if not form.startswith(word):
                continue
            suffix = form.removeprefix(word)
            if suffix:
                kyrgyz_tili_dictionary_suffixes.add(suffix)

    print(f'[Suffixes] Dictionary (kyrgyz_tili) suffixes: {len(kyrgyz_tili_dictionary_suffixes)}')

    suffixes = suffixes.union(dictionary_suffixes)
    suffixes = suffixes.union(kyrgyz_tili_dictionary_suffixes)
    print(f'[Suffixes] Total suffixes: {len(suffixes)}')

    write_file(f'{file_location}/../results/suffixes.txt', '\n'.join(sorted(suffixes)))

    return SuffixTrie(suffixes)


if __name__ == '__main__':
    suffix_trie = get_suffix_trie()
