from copy import deepcopy
import requests
import json
import os


# https://github.com/tatuylonen/wiktextract
URL = 'https://kaikki.org/dictionary/Kyrgyz/kaikki.org-dictionary-Kyrgyz.jsonl'

ALLOWED_LETTERS = 'абвгдеёжзийклмнпрстуфхцчшъыьэюяңөү'
ALLOWED_LETTERS = tuple(ALLOWED_LETTERS + ALLOWED_LETTERS.upper())


def main():
    print('Starting...')

    if not os.path.isfile('results/kaikki.org-dictionary-Kyrgyz.jsonl'):
        print('Downloading dictionary...')
        response = requests.get(URL)
        with open('results/kaikki.org-dictionary-Kyrgyz.jsonl', 'wb') as file:
            file.write(response.content)

    with open('results/kaikki.org-dictionary-Kyrgyz.jsonl', 'r', encoding='utf-8') as file:
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

    with open('results/akaikki.org-dictionary-Kyrgyz.pretty.jsonl', 'w', encoding='utf-8') as file:
        for word in words:
            file.write(json.dumps(word, ensure_ascii=False, indent=4) + '\n')

    # print(words[2000])

    # with open('results/tmp.json', 'w', encoding='utf-8') as file:
    #     json.dump(words[2000], file, ensure_ascii=False, indent=4)

    with open('results/all_words_from_dictionary.txt', 'w', encoding='utf-8') as file:
        for word in words:
            file.write(
                word['word']
                # + '\t'
                + '\n'
            )

    # words_by_word = {word['word']: word for word in words}
    pre_words_by_base = {}

    for word in words:
        pre_words_by_base[word['word']] = set()

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

            if word_form['form'] in pre_words_by_base:
                continue

            pre_words_by_base[word['word']].add(word_form['form'])

        pre_words_by_base[word['word']] = sorted(pre_words_by_base[word['word']])

    # print(pre_words_by_base)

    words_by_base = deepcopy(pre_words_by_base)

    for word, forms in pre_words_by_base.items():
        for form in forms:
            if form in words_by_base:
                del words_by_base[form]

    print(f'Total word bases: {len(words_by_base)}')
    print(f'Total word forms: {sum(len(forms) for forms in words_by_base.values()) + len(words_by_base)}')

    # print(words_by_base)

    with open('results/all_words_from_dictionary_by_base.txt', 'w', encoding='utf-8') as file:
        for word, forms in words_by_base.items():
            file.write('\n├╴'.join([word] + forms) + '\n\n')


if __name__ == '__main__':
    main()
