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

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    def parsear_fecha(self, entrada):
        return dateutil.parser.parse(entrada.updated)

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
                fecha = dateutil.parser.parse(entrada.published)  - datetime.timedelta(hours=3)
                url = entrada.link
                # self.categorias[tag].append(Noticia(titulo, texto, fecha, url))
                self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=tag, titulo=titulo, texto=texto))

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self, "paginadoce")
    
    def parsear_fecha(self, entrada):
        return datetime.datetime.today()

class ElDestape(Diario):

    def __init__(self):
        Diario.__init__(self, "eldestape")

    def reconocer_urls_y_fechas_noticias(self, url_feed):
        urls_y_fechas = []
        feed = bs(urllib.request.urlopen(url_feed).read(), 'html.parser')
        for elemento_url in feed.find_all('url'):
            url = elemento_url.loc.string
            fecha = dateutil.parser.parse(elemento_url.find('news:publication_date').string) - datetime.timedelta(hours=3)
            urls_y_fechas.append((url, fecha))
        return urls_y_fechas