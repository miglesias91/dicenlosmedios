import unittest

import newspaper as np

from medios.diarios.casarosada import CasaRosada

class TestAmbito(unittest.TestCase):

    def test_parsear_entradas(self):
        cr = CasaRosada()
        cr.leer_historico()
        return 1

    def test_parsear_url_discursos(self):
        cr = CasaRosada()
        cr.parsear_urls_discursos([])
        return 1

    def test_parsear_discursos(self):
        cr = CasaRosada()
        cr.parsear_discursos([])
        return 1