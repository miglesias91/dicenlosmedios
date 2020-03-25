import unittest

import newspaper as np

from medios.diarios.popular import Popular

class TestPopular(unittest.TestCase):

    def test_tuplas(self):
        popu = Popular()
        tuplas = popu.getTuplas()
        return 1 == tuplas.size()