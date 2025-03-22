import re
import os


file_location = os.path.dirname(os.path.abspath(__file__))


class Tokenizer:
    REPLACEMENTS = {
        'c': 'с',
        'o': 'о',
        'p': 'р',
        'a': 'а',
        'e': 'е',
        'y': 'у',

        # 'ё': 'е',
        # 'ң': 'н',
        # 'ө': 'о',
        # 'ү': 'у',

        # '-': None,
        # '–': None,
        # '—': None,
    }
    REPLACEMENTS.update({k.upper(): (v.upper() if v else v) for k, v in REPLACEMENTS.items()})
    TRANSLATION_TABLE = str.maketrans(REPLACEMENTS)

    # WORD_PATTERN = re.compile(r'\b[А-Яа-я]+(?:[-–—][А-Яа-я]+)*\b')
    WORD_PATTERN = re.compile(
        r'\d+-[а-яА-ЯёңөүЁҢҮӨ]+|\d+|[а-яА-ЯёңөүЁҢҮӨa-zA-Z\d\.\,]+\b'
    )

    # INNER_CLEAN_PATTERN = re.compile(r'[-–—]')

    SENTENCE_SPLIT_PATERN = re.compile(
        r'(?:\.+\s+(?=[А-ЯЁҢҮӨ]|[^\w\s]))|'
        r'(?:(?<=[а-яёңүө])\.+\s*(?=[А-ЯЁҢҮӨ]|[^\w\s]))|'
        r'[\|\(\)\[\]\{\}\…]+|'
        r'(?:\n(?=[А-ЯЁҢҮӨ]|[^\w\s]))|'
        r'(?:\:(?=\D))'
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

    print(tokenizer.SENTENCE_SPLIT_PATERN.pattern)
    print(tokenizer.WORD_PATTERN.pattern)

    # for filename in ('1474.txt',):
    for filename in os.listdir(f'{file_location}/../results/texts'):
        with open(f'{file_location}/../results/texts/{filename}', 'r', encoding='utf-8') as file:
            text = file.read()
            # print(text)

            for sentence in tokenizer.process_text(text):
                # print(sentence)
                for word in sentence:
                    assert ' ' not in word, filename
