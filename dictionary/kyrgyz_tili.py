from itertools import islice
import sys
import os

ROOT = '../'
sys.path.append(ROOT)

from src.utils import mkpath

sys.path.append('kyrgyz_tili')
import kg.db.generate_words as kyrgyz_tili_generate


def gen():
    print('Generating dictionary from kyrgyz_tili...')

    bases_count = forms_count = 0

    with open(mkpath(ROOT, 'results/kyrgyz_tili_words_by_base.txt'), 'w', encoding='utf-8') as file:
        os.chdir('kyrgyz_tili')
        for word in kyrgyz_tili_generate.Word.select():
            forms = kyrgyz_tili_generate.generate_all_children(word)
            bases_count += 1
            forms_count += len(forms)
            file.write(word.word + ''.join(
                f'\n├╴{form}' for form in islice(forms, 1, None)
            ) + '\n\n')

    print(f'Total word bases: {bases_count}')
    print(f'Total word forms: {forms_count}')


if __name__ == '__main__':
    gen()
