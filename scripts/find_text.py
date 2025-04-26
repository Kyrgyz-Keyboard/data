from concurrent.futures import ThreadPoolExecutor
import sys
import os

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


def find_word_in_file(text_num: int, word: str) -> tuple[str, str] | None:
    path = mkpath(f'../results/texts/{text_num}.txt')
    if not os.path.exists(path):
        return None

    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        if word in content:
            return path, content

    return None


def find_word(word: str):
    max_num = max(int(filename.removesuffix('.txt')) for filename in os.listdir(mkpath('../results/texts')))
    print(max_num)

    with ThreadPoolExecutor(max_workers=1_000) as executor:
        for future in (
            executor.submit(find_word_in_file, text_num, word)
            for text_num in range(607381, max_num + 1)
        ):
            result = future.result()
            if result is not None:
                path, content = result
                print('Found in file:', path)
                print(content)
                break


if __name__ == '__main__':
    find_word('мындан бир нечеге')
