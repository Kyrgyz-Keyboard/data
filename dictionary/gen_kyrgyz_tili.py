from itertools import islice
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

with mkpath.import_from('kyrgyz_tili'):
    from kg.db import generate_words


def gen():
    print('Generating dictionary from kyrgyz_tili...')

    bases_count = forms_count = 0

    with open(mkpath('../results/kyrgyz_tili_words_by_base.txt'), 'w', encoding='utf-8') as file, \
            mkpath.chdir('kyrgyz_tili'):

        for word in generate_words.Word.select():
            forms = generate_words.generate_all_children(word)
            bases_count += 1
            forms_count += len(forms)
            file.write(word.word + ''.join(
                f'\n├╴{form}' for form in islice(forms, 1, None)
            ) + '\n\n')

    print(f'Total word bases: {bases_count}')
    print(f'Total word forms: {forms_count}')


if __name__ == '__main__':
    gen()
