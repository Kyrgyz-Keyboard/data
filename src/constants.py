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

SUFFIXES = [
    'чы',
    'чи',
    'чу',
    'чү',
    'ба',
    'бе',
    'бо',
    'бө',
    'мын',
    'мин',
    'мун',
    'мүн',
    'сың',
    'сиң',
    'суң',
    'сүң',
    'сыз',
    'сиз',
    'суз',
    'сүз',
    'быз',
    'биз',
    'буз',
    'бүз',
    'пыз',
    'пиз',
    'пуз',
    'пүз',
    'сыңар',
    'сиңер',
    'суңар',
    'сүңөр',
    'сыздар',
    'сиздер',
    'суздар',
    'сүздөр',
    'нын',
    'нин',
    'нун',
    'нүн',
    'дын',
    'дин',
    'дун',
    'дүн',
    'тын',
    'тин',
    'тун',
    'түн',
    'га',
    'ге',
    'го',
    'гө',
    'ка',
    'ке',
    'ко',
    'кө',
    'дар',
    'дер',
    'дор',
    'дөр',
    'тар',
    'тер',
    'тор',
    'төр',
    'лар',
    'лер',
    'лор',
    'лөр'
]
SUFFIXES = tuple(set(suffix.translate(TRANSLATION_TABLE) for suffix in SUFFIXES))


def remove_suffixes(word: str) -> str:
    while True:
        for suffix in SUFFIXES:
            if word.endswith(suffix):
                word = word.removesuffix(suffix)
                break
        else:
            break
    return word
