from dataclasses import dataclass, field
from collections import defaultdict
import sys

if __name__ == '__main__':
    sys.path.append('../')

from src.utils import PathMagic
mkpath = PathMagic(__file__)


@dataclass
class TrieNode:
    own_freq: int = 0
    total_freq: int = 0
    children: dict[str, 'TrieNode'] = field(default_factory=lambda: defaultdict(TrieNode))

    def update(self):
        for node in self.children.values():
            node.update()

        self.total_freq = self.own_freq + sum(node.total_freq for node in self.children.values())

    def __getitem__(self, char: str) -> 'TrieNode':
        return self.children[char]


def build_trie() -> TrieNode:
    with open(mkpath('../results/word_freq.txt'), 'r', encoding='utf-8') as file:
        word_freq = {}
        for line in map(str.strip, filter(None, file)):
            word, tmp_freq = line.split()
            word_freq[word] = int(tmp_freq)

    sum_of_all_freq = 0

    trie = TrieNode()

    for word, freq in word_freq.items():
        sum_of_all_freq += freq

        node = trie
        for char in word:
            node = node[char]
        node.own_freq += freq

    trie.update()

    assert trie.total_freq == sum_of_all_freq, 'Total frequency mismatch, trie build failed'

    return trie


def predict_word(trie: TrieNode, word: str) -> list[tuple[int, str]]:
    node = trie
    for char in word:
        if char not in node.children:
            return []
        node = node[char]

    words = []

    def traverse(node: TrieNode, prefix: str):
        if node.own_freq:
            words.append((node.own_freq, prefix))
        for char, child_node in node.children.items():
            traverse(child_node, prefix + char)

    traverse(node, word)

    words.sort(key=lambda x: x[0], reverse=True)

    return words[:5]


def predict_letteer(trie: TrieNode, word: str) -> list[tuple[int, str]]:
    node = trie
    for char in word:
        if char not in node.children:
            return []
        node = node[char]

    letters = [
        (next_node.total_freq, char)
        for char, next_node in node.children.items()
    ]

    letters.sort(key=lambda x: x[0], reverse=True)

    return letters[:5]


if __name__ == '__main__':
    trie = build_trie()

    print('Top 5 words to complete:')
    print(predict_word(trie, 'Рес'))

    print('Top 5 letters to complete:')
    print(predict_letteer(trie, 'Рес'))
