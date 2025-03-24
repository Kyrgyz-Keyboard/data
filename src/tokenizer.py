import re
import os


file_location = os.path.dirname(os.path.abspath(__file__))


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
         (?:[0-9]+-[а-яА-ЯёңөүЁҢҮӨa-zA-Z]+)
        |(?:(?:[а-яА-ЯёңөүЁҢҮӨa-zA-Z0-9\.]+)(?:,[0-9]+)?\b)
        """,
        flags=re.VERBOSE
    )

    # INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

    SENTENCE_SPLIT_PATERN = re.compile(
        r"""
         (?:\.+\s+(?=[A-ZА-ЯЁҢҮӨ]|[^\w\s]))
        |(?:(?<=[a-zа-яёңүө ])\.{2,})
        |(?:(?<=[a-zа-яёңүө ])\.\s*(?=[A-ZА-ЯЁҢҮӨ]|[^\w\s]))
        |[\|\(\)\[\]\{\}\…]+
        |(?:\n(?=[a-zа-яA-ZА-ЯЁҢҮӨ]|[^\w\s]))
        |(?:\:(?=[^0-9]))
        """,
        flags=re.VERBOSE
    )

    def __init__(self):
        pass

    def process_text(self, text: str):
        for sentence in Tokenizer.SENTENCE_SPLIT_PATERN.split(text.translate(Tokenizer.TRANSLATION_TABLE)):
            words = []
            for word in map(re.Match.group, Tokenizer.WORD_PATTERN.finditer(sentence)):
                if len(word) > 1:
                    words.append(word)
            if words:
                yield words


if __name__ == '__main__':
    tokenizer = Tokenizer()

    # print(tokenizer.SENTENCE_SPLIT_PATERN.pattern)
    # print(tokenizer.WORD_PATTERN.pattern)

    # for filename in os.listdir(f'{file_location}/../results/texts'):
    for filename in ('28158.txt',):
        with open(f'{file_location}/../results/texts/{filename}', 'r', encoding='utf-8') as file:
            text = file.read()
            # print(text)

            for sentence in tokenizer.process_text(text):
                # print(sentence)
                for word in sentence:
                    assert ' ' not in word, filename


# Check on:
# 28158 - Runaway REGEX
