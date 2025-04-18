import sys
import re

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


class Tokenizer:
    REPLACEMENTS = {
        # 'c': 'с',
        # 'o': 'о',
        # 'p': 'р',
        # 'a': 'а',
        # 'e': 'е',
        # 'y': 'у',

        # 'ё': 'е',
        # 'ң': 'н',
        # 'ө': 'о',
        # 'ү': 'у',

        'ѳ': 'ө',  # Careful! Renders the same

        # '-': None,
        # '–': None,
        # '—': None,
    }
    REPLACEMENTS.update({k.upper(): (v.upper() if v else v) for k, v in REPLACEMENTS.items()})
    TRANSLATION_TABLE = str.maketrans(REPLACEMENTS)

    # WORD_PATTERN = re.compile(r'\b[А-Яа-я]+(?:[-–—][А-Яа-я]+)*\b')
    WORD_PATTERN = re.compile(
        r"""
        (?:
        # Main pattern
          [а-яa-zёңөүА-ЯA-ZЁҢҮӨ](?:[а-яa-zёңөүА-ЯA-ZЁҢҮӨ\.\:]*[а-яa-zёңөүА-ЯA-ZЁҢҮӨ])?
        # Pure numbers + (23:59) + (1.5 / 1,5)
        | [0-9](?:[0-9\:\.\,]*[0-9])?
        ) (?=\b|\d)
        """,
        flags=re.VERBOSE
    )

    # INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

    SENTENCE_SPLIT_PATERN = re.compile(
        r"""
        # Linebreak is always a separator
          \n
        # Weird (and not so) symbols are contextual separators
        | [\!\?\|\(\)\[\]\{\}\…\\\/\•\。\︖\︕\？\！\⁇\⁈\⁉\؟\¿\¡\।\॥\።\⸮]+
        # Colon with anything except digit afterward (to discard 00:00)
        | \:(?=[^0-9])
        # Ellipsis and other instances of multiple dots are always separators
        | \.{2,}
        # Dot after lowercase that follows with an uppercase letter or weired symbol
        | (?<=[a-zа-яёңүө ])\.\s*(?=[A-ZА-ЯЁҢҮӨ]|[^\w\s])
        # Dot after uppercase that follows with a lowercase letter or weired symbol
        | (?<=[A-ZА-ЯЁҢҮӨ ])\.\s*(?=[a-zа-яёңүө]|[^\w\s])
        # Dot after digit that follows with any letter
        | (?<=\d)\.\s*(?=[a-zа-яёңүөA-ZА-ЯЁҢҮӨ]|[^\w\s])
        """,
        flags=re.VERBOSE
    )

    def __init__(self):
        pass

    def process_text(self, text: str):
        for sentence in filter(None, map(str.strip, Tokenizer.SENTENCE_SPLIT_PATERN.split(
            text.translate(Tokenizer.TRANSLATION_TABLE)
        ))):
            words = []
            for word in map(re.Match.group, Tokenizer.WORD_PATTERN.finditer(sentence)):
                if len(word) > 1 or word.isdigit():
                    words.append(word)
            if words:
                yield words


if __name__ == '__main__':
    tokenizer = Tokenizer()

    # print(tokenizer.SENTENCE_SPLIT_PATERN.pattern)
    # print(tokenizer.WORD_PATTERN.pattern)

    # for filename in os.listdir(f'{file_location}/../results/texts'):
    for filename in ('test.txt',):
        with open(mkpath(f'../results/{filename}'), 'r', encoding='utf-8') as file:
            text = file.read()
            # print(text)

            for sentence in tokenizer.process_text(text):
                # print(sentence)
                for word in sentence:
                    assert ' ' not in word, filename


# Check on:
# 28158 - Runaway REGEX
