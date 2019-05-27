import dateutil
import datetime
import re
import feedparser as fp
import urllib.request
from bs4 import BeautifulSoup as bs

from medios.diarios.diario import Diario
from medios.diarios.noticia import Noticia

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self, "clarin")

    # def reconocer_urls_noticias(self, url_feed):
    #     urls = []
    #     for entrada in fp.parse(url_feed).entries:
    #         urls.append(entrada.link)
    #     return urls

    # def nueva_noticia(self, url):
    #     articulo = np.Article(url=url, language='es')
    #     articulo.download()
    #     articulo.parse()
    #     return Noticia(articulo.title, articulo.text, articulo.publish_date, url)

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    def parsear_fecha(self, entrada):
        return dateutil.parser.parse(entrada.updated)

    # def reconocer_urls_noticias(self, url_feed):
    #     urls = []
    #     for entrada in fp.parse(url_feed).entries:
    #         urls.append(entrada.link)
    #     return urls

    # def nueva_noticia(self, url):
    #     articulo = np.Article(url=url, language='es')
    #     articulo.download()
    #     articulo.parse()
    #     return Noticia(articulo.title, articulo.text, articulo.publish_date, url)

class Infobae(Diario):

    def __init__(self):
        Diario.__init__(self, "infobae")

    def leer(self):
        tag_regexp = re.compile(r'<[^>]+>')
        for tag, url_feed in self.feeds.items():
            self.categorias[tag] = []
            for entrada in fp.parse(url_feed).entries:
                titulo = entrada.title
                texto = re.sub(tag_regexp,'',entrada.content[0].value)
                fecha = dateutil.parser.parse(entrada.published)
                url = entrada.link
                self.categorias[tag].append(Noticia(titulo, texto, fecha, url))

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self, "paginadoce")
    
    def parsear_fecha(self, entrada):
        return datetime.datetime.today()
    # def reconocer_urls_noticias(self, url_feed):
    #     urls = []
    #     for entrada in fp.parse(url_feed).entries:
    #         urls.append(entrada.link)
    #     return urls

    # def nueva_noticia(self, url):
    #     articulo = np.Article(url=url, language='es')
    #     articulo.download()
    #     articulo.parse()
    #     return Noticia(articulo.title, articulo.text, articulo.publish_date, url)

class ElDestape(Diario):

    def __init__(self):
        Diario.__init__(self, "eldestape")

    def reconocer_urls_y_fechas_noticias(self, url_feed):
        urls_y_fechas = []
        feed = bs(urllib.request.urlopen(url_feed).read(), 'html.parser')
        for elemento_url in feed.find_all('url'):
            url = elemento_url.loc.string
            fecha = dateutil.parser.parse(elemento_url.find('news:publication_date').string)
            urls_y_fechas.append((url, fecha))
        return urls_y_fechas
    #     articulo = np.Article(url=url, language='es')
    #     articulo.download()
    #     articulo.parse()
    #     return Noticia(articulo.title, articulo.text, articulo.publish_date, url)