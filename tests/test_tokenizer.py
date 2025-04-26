import jstyleson as json
import pytest
import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)

from src.tokenizer import Tokenizer


tokenizer = Tokenizer()


def get_test_cases():
    all_files = os.listdir(mkpath('data'))
    cases = []
    for filename in all_files:
        if filename.endswith('.txt'):
            case_name = filename[:-4]
            if os.path.exists(mkpath(f'data/{case_name}.result.json')):
                cases.append(case_name)
    return cases


@pytest.mark.parametrize('case_name', get_test_cases())
def test_tokenizer_case(case_name):
    with open(mkpath(f'data/{case_name}.txt'), encoding='utf-8') as f:
        text = f.read()

    with open(mkpath(f'data/{case_name}.result.json'), encoding='utf-8') as f:
        expected = json.load(f)

    output = list(tokenizer.process_text(text))

    assert output == expected, f'\n{output}\n\n{expected}'


if __name__ == '__main__':
    for case_name in get_test_cases():
        test_tokenizer_case(case_name)
