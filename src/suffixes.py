from functools import cache
import sys

import apertium

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from src.get_dictionary import get_kaikki_tili, get_kyrgyz_tili
from src.tokenizer import Tokenizer
from src.utils import write_file


class SuffixTrie:
    TrieType = dict[str, 'TrieType']

    def __init__(self):
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

        write_file(mkpath('../results/suffixes.txt'), '\n'.join(sorted(suffixes)))

        self.trie: SuffixTrie.TrieType = {}
        for suffix in suffixes:
            node: SuffixTrie.TrieType = self.trie
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


# class ApertiumWrapper:
#     def __init__(self):
#         self.analyzer = apertium.Analyzer('kir')

#     @cache  # noqa
#     def remove_suffix(self, word: str):
#         return min(
#             reading[0].baseform.lstrip('*')
#             for reading in self.analyzer.analyze(word)[0].readings
#         )


# def _convert_apertium():
#     from collections import defaultdict
#     import apertium

#     class ApertiumWrapper:
#         def __init__(self):
#             self.analyzer = apertium.Analyzer('kir')

#         @cache  # noqa
#         def remove_suffix(self, word: str):
#             return min(
#                 reading[0].baseform.lstrip('*')
#                 for reading in self.analyzer.analyze(word)[0].readings
#             )

#     apertium_analyzer = ApertiumWrapper()
#     freq_cap = 3000

#     # ------------

#     with open(mkpath('../results/base_simple_freq.txt'), 'r', encoding='utf-8') as file:
#         base_simple_freq = {}
#         for line in filter(None, file):
#             base, freq = line.split(' ')
#             if int(freq) < freq_cap:
#                 break
#             base_simple_freq[base] = int(freq)

#     base_simple_freq_sorted = sorted(base_simple_freq.items(), key=lambda x: x[1], reverse=True)
#     del base_simple_freq

#     write_file(
#         '../results/tmp.base_simple_freq.txt',
#         '\n'.join(f'{base} {freq}' for base, freq in base_simple_freq_sorted)
#     )

#     # ------------

#     with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
#         word_freq = {}
#         for line in filter(None, file):
#             word, freq = line.split(' ')
#             if int(freq) < freq_cap:
#                 break
#             word_freq[word] = int(freq)

#     word_freq_sorted = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
#     del word_freq

#     write_file(
#         '../results/tmp.word_freq.txt',
#         '\n'.join(f'{word} {freq}' for word, freq in word_freq_sorted)
#     )

#     # ------------

#     with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
#         base_apertium_freq: dict[str, int] = defaultdict(int)
#         for i, line in enumerate(filter(None, file), 1):
#             word, freq = line.split(' ')
#             if int(freq) < freq_cap:
#                 break
#             base = apertium_analyzer.remove_suffix(word)
#             base_apertium_freq[base] += int(freq)
#             if i % 100 == 0:
#                 print(i, int(freq), word, base)

#     base_apertium_freq_sorted = sorted(base_apertium_freq.items(), key=lambda x: x[1], reverse=True)
#     del base_apertium_freq

#     write_file(
#         '../results/tmp.base_apertium_freq.txt',
#         '\n'.join(f'{base} {freq}' for base, freq in base_apertium_freq_sorted)
#     )


if __name__ == '__main__':
    suffix_trie = SuffixTrie()
    print(suffix_trie.remove_suffix('китептеримдин'))
    print(suffix_trie.remove_suffix('кыргызча'))

    apertium_analyzer = ApertiumWrapper()
    print(apertium_analyzer.remove_suffix('китептеримдин'))
    print(apertium_analyzer.remove_suffix('кыргызча'))

    # _convert_apertium()
