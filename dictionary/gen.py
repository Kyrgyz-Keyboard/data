import sys

if __name__ == '__main__':
    sys.path.append('../')

from dictionary.gen_kaikki import gen as gen_kaikki
from dictionary.gen_kyrgyz_tili import gen as gen_kyrgyz_tili


def gen_all():
    gen_kaikki()
    gen_kyrgyz_tili()


if __name__ == '__main__':
    gen_all()
