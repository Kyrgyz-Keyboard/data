class TrieNode:
	def __init__ (self):
		self.children = {}
		self.dict = {}

class Trie:
	def __init__ (self):
		self.root = TrieNode()

	def insert (self, word, word2):
		node = self.root
		for l in word:
			if l not in node.children:
				node.children[l] = TrieNode()
			node = node.children[l]
		if word2 not in node.dict:
			node.dict[word2] = 0
		else:
			node.dict[word2] += 1

	def get_three_words (self, words):
		node = self.find_node(words)
		if node:
			mx1 = 0
			mx2 = 0
			mx3 = 0
			answers = []
			ans1 = ""
			ans2 = ""
			ans3 = ""
			for i in node.dict.keys():
				if node.dict[i] > mx1:
					ans1 = i
					mx1 = node.dict[i]
			for i in node.dict.keys():
				if i != ans1 and node.dict[i] > mx2:
					ans2 = i
					mx2 = node.dict[i]
			for i in node.dict.keys():
				if i != ans1 and i != ans2 and node.dict[i] > mx3:
					ans3 = i
					mx3 = node.dict[i]
			answers.append(ans1)
			answers.append(ans2)
			answers.append(ans3)
			return answers
		return None

	def find_node(self, words):
		node = self.root
		for l in words:
			if l not in node.children:
				return None
			node = node.children[l]
		return node

class TextProcessor:
	def __init__ (self, text):
		self.trie = Trie()
		self.text = text
		self.words = text.split(' ')
		self.update_trie()
	def update_trie (self):
		for i in range(len(self.words) - 3):
			words_before = self.words[i] + ' ' + self.words[i + 1] + ' ' + self.words[i + 2]
			cur_word = self.words[i + 3]
			self.trie.insert(words_before, cur_word)
	def get_likeliest_next_words (self, words):
		return self.trie.get_three_words(words)