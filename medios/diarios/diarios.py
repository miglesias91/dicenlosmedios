import dateutil
import re
import feedparser as fp
import newspaper as np
import urllib.request
from bs4 import BeautifulSoup as bs
from datetime import datetime

from medios.diarios.diario import Diario
from medios.diarios.noticia import Noticia

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self, "clarin")

    # def leer(self):
    #     for tag, url in self.feeds.items():
    #         entradas = fp.parse(url)
    #         for entrada in entradas.entries:
    #             art = np.Article(url=entrada.link, language='es')
    #             art.download()
    #             art.parse()
    #             art.nlp()

    def reconocer_urls_noticias(self, url_feed):
        urls = []
        for entrada in fp.parse(url_feed).entries:
            urls.append(entrada.link)
        return urls

    def nueva_noticia(self, url):
        articulo = np.Article(url=url, language='es')
        articulo.download()
        articulo.parse()
        articulo.nlp()
        return Noticia(articulo.title, articulo.text, articulo.top_image, articulo.tags, articulo.authors, articulo.keywords, articulo.publish_date)

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    # def leer(self):
    #     for tag, url in self.feeds.items():
    #         entradas = fp.parse(url)
    #         for entrada in entradas.entries:
    #             art = np.Article(url=entrada.link, language='es')
    #             art.download()
    #             art.parse()
    #             art.nlp()

    def reconocer_urls_noticias(self, url_feed):
        urls = []
        for entrada in fp.parse(url_feed).entries:
            urls.append(entrada.link)
        return urls

    def nueva_noticia(self, url):
        articulo = np.Article(url=url, language='es')
        articulo.download()
        articulo.parse()
        articulo.nlp()
        return Noticia(articulo.title, articulo.text, articulo.top_image, articulo.tags, articulo.authors, articulo.keywords, articulo.publish_date)

class Infobae(Diario):

    def __init__(self):
        Diario.__init__(self, "infobae")

    def leer(self):
        tag_regexp = re.compile(r'<[^>]+>')
        for tag, url_feed in self.feeds.items():
            for entrada in fp.parse(url_feed).entries:
                titulo = entrada.title
                texto = re.sub(tag_regexp,'',entrada.content[0].value)
                fecha = dateutil.parser.parse(entrada.published)
                self.categorias[tag].append(Noticia(titulo, texto, '', [], [], [], fecha))

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self, "paginadoce")

    # def leer(self):
    #     for tag, url in self.feeds.items():
    #         entradas = fp.parse(url)
    #         for entrada in entradas.entries:
    #             noticia = self.nueva_noticia
    #             art = np.Article(url=entrada.link, language='es')
    #             art.download()
    #             art.parse()
    #             art.nlp()

    def reconocer_urls_noticias(self, url_feed):
        urls = []
        for entrada in fp.parse(url_feed).entries:
            urls.append(entrada.link)
        return urls

    def nueva_noticia(self, url):
        articulo = np.Article(url=url, language='es')
        articulo.download()
        articulo.parse()
        articulo.nlp()
        return Noticia(articulo.title, articulo.text, articulo.top_image, articulo.tags, articulo.authors, articulo.keywords, articulo.publish_date)

class ElDestape(Diario):

    def __init__(self):
        Diario.__init__(self, "eldestape")
        
    # def leer(self):
    #     for tag, url in self.feeds.items():
    #         feed = bs(urllib.request.urlopen(url).read(), 'html.parser')
    #         for url in feed.find_all('loc'):
    #             art = np.Article(url=url.string, language='es')
    #             art.download()
    #             art.parse()
    #             art.nlp()

    def reconocer_urls_noticias(self, url_feed):
        feed = bs(urllib.request.urlopen(url_feed).read(), 'html.parser')
        return feed.find_all('loc')

    def nueva_noticia(self, url):
        articulo = np.Article(url=url, language='es')
        articulo.download()
        articulo.parse()
        articulo.nlp()
        return Noticia(articulo.title, articulo.text, articulo.top_image, articulo.tags, articulo.authors, articulo.keywords, articulo.publish_date)