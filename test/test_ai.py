import codecs
import string

import unittest

import nltk
from nltk.corpus import cess_esp

from ia.txt import freq, word2vec, word2vec_pro

class TestFreq(unittest.TestCase):

    def test_freq(self):
        texto = codecs.open("test/alicia.txt", 'r').read()

        textos = [texto, texto]

        fqs = freq(textos)

        self.assertEqual(fqs["alicia"], 872)

    def test_word2vec(self):
        texto = codecs.open("test/alicia.txt", 'r').read()

        textos = [texto]
        modelo = word2vec(textos)

        print(modelo.wv.most_similar('alicia', topn=5))

        self.assertEqual(1, 1)

    def test_word2vec_pro(self):
        texto = codecs.open("test/alicia.txt", 'r').read()

        textos = [texto]
        modelo = word2vec_pro(textos)
        print(modelo.wv.most_similar('alicia', topn=5))
        print(modelo.wv.most_similar('gato', topn=5))

    def test_stopwords(self):
        locales_stopwords = codecs.open("stopwords.txt", 'r', encoding="utf-8").read().split("\r\n")
        pass

if __name__ == '__main__':
    unittest.main()