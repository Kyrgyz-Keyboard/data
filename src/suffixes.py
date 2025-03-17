import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.constants import get_dictionary, TRANSLATION_TABLE


class SuffixTrie:
    def __init__(self, suffixes: set[str]):
        self.trie = {}
        for suffix in suffixes:
            node = self.trie
            for char in reversed(suffix):
                node = node.setdefault(char, {})
            node['$'] = suffix

    def remove_suffix(self, word: str) -> str:
        node = self.trie
        for i in range(len(word) - 1, -1, -1):
            char = word[i]
            if char not in node:
                break
            node = node[char]
            if '$' in node:
                return word[:i]
        return word


def get_suffix_trie() -> SuffixTrie:
    dictionary, _ = get_dictionary()

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
        'ка', 'ке', 'ко', 'кө',
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

        'ум', 'үм', 'өм'
    }
    handmade_suffixes = {suffix.translate(TRANSLATION_TABLE) for suffix in handmade_suffixes}

    print(f'[Suffixes] Hand-made suffixes: {len(handmade_suffixes)}')

    dictionary_suffixes = set()
    for word, forms in dictionary.items():
        for form in forms:
            if not form.startswith(word):
                continue
            suffix = form.removeprefix(word)
            if suffix:
                dictionary_suffixes.add(suffix)

    print(f'[Suffixes] Dictionary suffixes: {len(dictionary_suffixes)}')

    SUFFIXES = handmade_suffixes.union(dictionary_suffixes)
    suffix_trie = SuffixTrie(SUFFIXES)

    print(f'[Suffixes] Total suffixes: {len(SUFFIXES)}')

    return suffix_trie


def remove_suffixes(suffix_trie: SuffixTrie, word: str) -> str:
    return suffix_trie.remove_suffix(word)


if __name__ == '__main__':
    suffix_trie = get_suffix_trie()
