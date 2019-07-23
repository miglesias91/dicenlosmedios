import unittest

import newspaper as np

from medios.diarios.paginadoce import PaginaDoce

class TestPaginaDoce(unittest.TestCase):

    def test_entradas_feed(self):
        p12 = PaginaDoce()
        url_fecha_titulo_categoria = p12.entradas_feed()
        return len(url_fecha_titulo_categoria) == 1000

    def test_parsear_noticia(self):
        p12 = PaginaDoce()
        categoria, titulo, texto = p12.parsear_noticia(url="https://www.pagina12.com.ar/207920-ricky-martin-al-frente-de-las-manifestaciones-en-puerto-rico")
        return 1