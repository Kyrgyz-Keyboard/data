import re

REPLACEMENTS = {
    'c': 'с',
    'o': 'о',
    'p': 'р',
    'a': 'а',
    'e': 'е',
    'y': 'у',

    'ё': 'е',
    'ң': 'н',
    'ө': 'о',
    'ү': 'у',
}
REPLACEMENTS.update({v.upper(): k.upper() for k, v in REPLACEMENTS.items()})
TRANSLATION_TABLE = str.maketrans(REPLACEMENTS)

# WORD_PATTERN = re.compile(r'\b[А-Яа-я]+(?:[-–—][А-Яа-я]+)*\b')
WORD_PATTERN = re.compile(r'\b[А-Яа-яcopaeyёңөү]+(?:[-–—][А-Яа-яcopaeyёңөү]+)*\b')

INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

# ======================================================================================================================


class SuffixTrie:
    def __init__(self, suffixes: set[str]):
        self.trie = {}
        for suffix in suffixes:
            node = self.trie
            for char in reversed(suffix):  # Идём с конца
                node = node.setdefault(char, {})
            node['$'] = suffix  # Маркер конца суффикса

    def remove_suffix(self, word: str) -> str:
        node = self.trie
        for i in range(len(word) - 1, -1, -1):  # Проходим слово с конца
            char = word[i]
            if char not in node:
                break  # Суффикс не найден — выходим
            node = node[char]
            if '$' in node:
                return word[:i]  # Обрезаем найденный суффикс
        return word  # Если ничего не нашли — возвращаем как есть


SUFFIXES = {
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
SUFFIXES = {suffix.translate(TRANSLATION_TABLE) for suffix in SUFFIXES}
suffix_trie = SuffixTrie(SUFFIXES)


def remove_suffixes(word: str) -> str:
    return suffix_trie.remove_suffix(word)
