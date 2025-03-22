from spacy.lang.ky import Kyrgyz

nlp = Kyrgyz()

with open('results/texts/51721.txt', 'r', encoding='utf-8') as file:
    text = file.read()

nlp.add_pipe('sentencizer')

doc = nlp(text)
for sent in doc.sents:
    print(sent.text.strip())
    print()
