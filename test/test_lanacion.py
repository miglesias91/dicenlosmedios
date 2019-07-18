import unittest

import yaml

import newspaper as np

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce, CasaRosada

class TestLaNacion(unittest.TestCase):

    def test_leer_deportes(self):
        noticias = []
        c = LaNacion()
        for url_noticia, fecha in c.reconocer_urls_y_fechas_noticias(url_feed="http://contenidos.lanacion.com.ar/herramientas/rss/categoria_id=131"):
            noticia = c.nueva_noticia(url=url_noticia, categoria="deportes", diario="clarin")
            noticias.append(noticia)
        return 1

    def test_leer_espectaculos(self):
        noticias = []
        l = LaNacion()
        for url_noticia, fecha in l.reconocer_urls_y_fechas_noticias(url_feed="http://contenidos.lanacion.com.ar/herramientas/rss/categoria_id=120"):
            noticia = l.nueva_noticia(url=url_noticia, categoria="espectaculos", diario="clarin")
            noticias.append(noticia)
        return 1

    def test_leer_cultura(self):
        l = LaNacion()

        noticias = []

        with open('medios/diarios/config.yaml', 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        for diario in config['diarios']:
            if diario['tag'] != l.etiqueta:
                continue
            for feed in diario['feeds']:
                l.feeds[feed['tag']] = feed['url']
                if 'filtro' in feed:
                    l.filtros[feed['tag']] = feed['filtro']

        filtro = None
        if 'cultura' in l.filtros:
            filtro = l.filtros['cultura']

        for url_noticia, fecha in l.reconocer_urls_y_fechas_noticias(url_feed="https://www.lanacion.com.ar/ln-news.xml", filtro=filtro):
            noticia = l.nueva_noticia(url=url_noticia, categoria="cultura", diario="clarin")
            noticias.append(noticia)
        return 1