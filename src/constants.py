import re
import os


file_location = os.path.dirname(os.path.abspath(__file__))


# ======================================================== REGEX ========================================================

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

    '-': '',
    '–': '',
    '—': '',
}
# REPLACEMENTS.update({k.upper(): v.upper() for k, v in REPLACEMENTS.items()})
TRANSLATION_TABLE = str.maketrans(REPLACEMENTS)

# WORD_PATTERN = re.compile(r'\b[А-Яа-я]+(?:[-–—][А-Яа-я]+)*\b')
WORD_PATTERN = re.compile(r'\b[а-я]+\b')

# INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

# ===================================================== DICTIONARY =====================================================


def get_dictionary() -> tuple[dict[str, list[str]], dict[str, str]]:
    print('[Dictionary] Loading kaikii dictionary...')
    pre_dictionary: list[tuple[str, list[str]]] = []
    with open(f'{file_location}/../results/kaikki_dictionary_by_base.txt', 'r', encoding='utf-8') as file:
        for line in filter(None, map(str.strip, file)):
            if not line.startswith('├╴'):
                pre_dictionary.append((line, []))
            else:
                pre_dictionary[-1][1].append(line.removeprefix('├╴'))

    print(f'[Dictionary] Base words: {len(pre_dictionary)}')

    word_to_base: dict[str, str] = {}
    for word, forms in pre_dictionary:
        word_to_base[word] = word
        for form in forms:
            # if form in word_to_base:
            #     print(form)
            word_to_base[form] = word

    print(f'[dictionary] Word forms: {len(word_to_base)}')

    dictionary: dict[str, list[str]] = dict(pre_dictionary)

    return dictionary, word_to_base


if __name__ == '__main__':
    get_dictionary()
