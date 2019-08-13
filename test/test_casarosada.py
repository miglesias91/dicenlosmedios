import json

import unittest

import newspaper as np

from medios.diarios.casarosada import CasaRosada

class TestCasaRosada(unittest.TestCase):

    def test_parsear_entradas(self):
        cr = CasaRosada()
        entradas = cr.parsear_entradas()
        print("entradas: " + str(len(entradas)))
        return 1

    def test_parsear_url_discursos(self):
        cr = CasaRosada()
        entradas = cr.parsear_entradas()
        urls_discursos = cr.parsear_urls_discursos(entradas)
        return 1

    def test_parsear_discursos(self):
        cr = CasaRosada()
        # entradas = cr.parsear_entradas()
        # urls_discursos = cr.parsear_urls_discursos(entradas)
        json.load()
        discursos = cr.parsear_discursos(urls_discursos)
        return 1