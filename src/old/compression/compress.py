import sys
import os

if __name__ == '__main__':
    sys.path.append('../')


from src.utils import PathMagic
mkpath = PathMagic(__file__)


from src.utils import write_file


class CustomEncoding:
    ENCODE_TABLE = (
        'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        'ңүө'
        'ҢҮӨ'
        '0123456789'
        ' ,.:'
        '\n'
    )

    ENCODE_TABLE_DICT = {char: index for index, char in enumerate(ENCODE_TABLE)}

    @classmethod
    def encode(cls, string: str) -> bytes:
        return bytes(cls.ENCODE_TABLE_DICT[char] for char in string)

    @classmethod
    def decode(cls, byte_string: bytes) -> str:
        return ''.join(cls.ENCODE_TABLE[byte] for byte in byte_string)


def compress_results():
    encoder = CustomEncoding()
    print(f'Total characters: {len(encoder.ENCODE_TABLE)}')

    for foldername in ('sentences', 'sentences_of_bases_simple'):
        for filename in os.listdir(mkpath('../results', foldername)):
            with open(mkpath(f'../results/{foldername}/{filename}'), 'r', encoding='utf-8') as file:
                encoded_text = encoder.encode(file.read())

                write_file(
                    mkpath(f'../results/{foldername}_compressed/{os.path.splitext(filename)[0]}.bin'),
                    encoded_text, binary=True
                )
                write_file(
                    mkpath(f'../results/{foldername}_compressed.bin'),
                    encoder.encode('\n'), append=True, binary=True
                )
                write_file(
                    mkpath(f'../results/{foldername}_compressed.bin'),
                    encoded_text, append=True, binary=True
                )

            print(f'Finished processing {mkpath(f"../results/{foldername}/{filename}")}')


if __name__ == '__main__':
    compress_results()
