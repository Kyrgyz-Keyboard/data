from kaikki import gen as kaikki_gen
from kyrgyz_tili import gen as kyrgyz_tili_gen


def gen_all():
    kaikki_gen()
    kyrgyz_tili_gen()


if __name__ == '__main__':
    gen_all()
