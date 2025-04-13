import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


def _get_dictionary_path(dictionary_name: str) -> str:
    return mkpath(f'../results/{dictionary_name}.txt')


def _load_file(dictionary_name) -> tuple[dict[str, list[str]], dict[str, str]]:
    print(f'[Dictionary] Loading {dictionary_name} dictionary...')

    pre_dictionary: list[tuple[str, list[str]]] = []

    with open(_get_dictionary_path(dictionary_name), 'r', encoding='utf-8') as file:
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


def get_kaikki_tili() -> tuple[dict[str, list[str]], dict[str, str]]:
    if not os.path.isfile(_get_dictionary_path('kaikki_words_by_base')):
        from dictionary.gen import gen_kaikki
        gen_kaikki()
    return _load_file('kaikki_words_by_base')


def get_kyrgyz_tili() -> tuple[dict[str, list[str]], dict[str, str]]:
    if not os.path.isfile(_get_dictionary_path('kyrgyz_tili_words_by_base')):
        from dictionary.gen import gen_kyrgyz_tili
        gen_kyrgyz_tili()
    return _load_file('kyrgyz_tili_words_by_base')


if __name__ == '__main__':
    get_kaikki_tili()
    get_kyrgyz_tili()
