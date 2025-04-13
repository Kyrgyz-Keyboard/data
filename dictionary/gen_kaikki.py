import json
import sys
import os

import requests

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


# https://github.com/tatuylonen/wiktextract
URL = 'https://kaikki.org/dictionary/Kyrgyz/kaikki.org-dictionary-Kyrgyz.jsonl'

ALLOWED_LETTERS = {letter for letter in 'абвгдеёжзийклмнпрстуфхцчшъыьэюяңөү' for letter in (letter, letter.upper())}


def gen():
    print('Generating dictionary from kaikki...')

    dictionary_path = mkpath('../results/kaikki.org-dictionary-Kyrgyz.jsonl')
    if not os.path.isfile(dictionary_path):
        print('Downloading dictionary...')
        with open(dictionary_path, 'wb') as file:
            file.write(requests.get(URL).content)

    with open(dictionary_path, 'r', encoding='utf-8') as file:
        data = list(map(json.loads, file))

    words = []

    for word in data:
        assert word['lang'] == 'Kyrgyz'
        assert word['lang_code'] == 'ky'

        if word['pos'] in ('character', 'suffix', 'phrase'):
            continue

        if not all(letter in ALLOWED_LETTERS for letter in word['word']):
            continue

        if word['word'] in ALLOWED_LETTERS:
            continue

        # if word['pos'] not in ('adv', 'det', 'conj', 'pron', 'noun', 'verb', 'name', 'num', 'intj', 'adj', 'postp'):
        #     print(word['pos'])

        # if word['pos'] in ('phrase', 'suffix'):
        #     print(word['pos'], word['word'])

        words.append(word)

    # pos = set()
    # for word in words:
    #     pos.add(word['pos'])

    words.sort(key=lambda word: word['word'])

    print(f'Initial words in dictionary: {len(words)}')

    with open(os.path.splitext(dictionary_path)[0] + '.pretty.jsonl', 'w', encoding='utf-8') as file:
        for word in words:
            file.write(json.dumps(word, ensure_ascii=False, indent=4) + '\n')

    # with open(mkpath('../results/kaikki_words.txt'), 'w', encoding='utf-8') as file:
    #     for word in words:
    #         file.write(
    #             word['word']
    #             # + '\t'
    #             + '\n'
    #         )

    words_by_base: dict[str, set[str]] = {}
    for word in words:
        words_by_base[word['word']] = set()

        for word_form in word['forms']:
            if word_form['form'] == word['word']:
                continue

            if any((
                'Arabic' in word_form['tags'],
                'romanization' in word_form['tags'],
                'table-tags' in word_form['tags'],
                'inflection-template' in word_form['tags'],
            )):
                continue

            if not all(letter in ALLOWED_LETTERS for letter in word_form['form']):
                continue

            if word_form['form'] in words_by_base:
                continue

            words_by_base[word['word']].add(word_form['form'])

    for word in list(words_by_base.keys()):
        for form in words_by_base.get(word, set()):
            if form in words_by_base:
                del words_by_base[form]

    print(f'Total word bases: {len(words_by_base)}')
    print(f'Total word forms: {sum(len(forms) for forms in words_by_base.values()) + len(words_by_base)}')

    with open(mkpath('../results/kaikki_words_by_base.txt'), 'w', encoding='utf-8') as file:
        for word, forms in words_by_base.items():
            file.write('\n├╴'.join([word] + sorted(forms)) + '\n\n')


if __name__ == '__main__':
    gen()
