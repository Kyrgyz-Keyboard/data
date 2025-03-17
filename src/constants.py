import re
import os


FILE_LOCATION = os.path.dirname(os.path.abspath(__file__))


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
}
REPLACEMENTS.update({v.upper(): k.upper() for k, v in REPLACEMENTS.items()})
TRANSLATION_TABLE = str.maketrans(REPLACEMENTS)

# WORD_PATTERN = re.compile(r'\b[А-Яа-я]+(?:[-–—][А-Яа-я]+)*\b')
WORD_PATTERN = re.compile(r'\b[А-Яа-яcopaeyёңөү]+(?:[-–—][А-Яа-яcopaeyёңөү]+)*\b')

INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

# ===================================================== DICTIONARY =====================================================

print('Loading dictionary...')
DICTIONARY = []
with open(f'{FILE_LOCATION}/../results/all_words_from_dictionary_by_base.txt', 'r', encoding='utf-8') as file:
    for line in filter(None, map(str.strip, file)):
        if not line.startswith('├╴'):
            DICTIONARY.append((line, []))
        else:
            DICTIONARY[-1][1].append(line.removeprefix('├╴'))

print(f'[Dictionary] Base words: {len(DICTIONARY)}')

WORD_TO_BASE = {}
for word, forms in DICTIONARY:
    WORD_TO_BASE[word] = word
    for form in forms:
        # if form in WORD_TO_BASE:
        #     print(form)
        WORD_TO_BASE[form] = word

print(f'[Dictionary] Word forms: {len(WORD_TO_BASE)}')
