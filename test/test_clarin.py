import unittest

import newspaper as np

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce, CasaRosada

class TestClarin(unittest.TestCase):

    def test_leer_deportes(self):
        noticias = []
        c = Clarin()
        for url_noticia, fecha in c.reconocer_urls_y_fechas_noticias(url_feed="https://www.clarin.com/rss/deportes/"):
            noticia = c.nueva_noticia(url=url_noticia, categoria="deportes", diario="clarin")
            noticias.append(noticia)
        return 1

    def test_leer_espectaculos(self):
        noticias = []
        c = Clarin()
        for url_noticia, fecha in c.reconocer_urls_y_fechas_noticias(url_feed="https://www.clarin.com/rss/espectaculos/"):
            noticia = c.nueva_noticia(url=url_noticia, categoria="espectaculos", diario="clarin")
            noticias.append(noticia)
        return 1

    def test_leer_cultura(self):
        noticias = []
        c = Clarin()
        for url_noticia, fecha in c.reconocer_urls_y_fechas_noticias(url_feed="https://www.clarin.com/rss/cultura/"):
            noticia = c.nueva_noticia(url=url_noticia, categoria="cultura", diario="clarin")
            noticias.append(noticia)
        return 1