import codecs
import string

import unittest

import nltk
from nltk.corpus import cess_esp

from ia.txt.freq import freq

class TestFreq(unittest.TestCase):

    def test_freq(self):
        texto = codecs.open("test/alicia.txt", 'r').read()

        textos = [texto, texto]

        fqs = freq(textos)

        # for word, frequency in fqs.most_common(50):
        #     print(u'{};{}'.format(word, frequency))

        self.assertEqual(fqs["alicia"], 872)
        self.assertEqual(fqs["dijo"], 542)


if __name__ == '__main__':
    unittest.main()