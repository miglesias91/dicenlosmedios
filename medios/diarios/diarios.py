import dateutil
import datetime
import re
import feedparser as fp
import urllib.request
from bs4 import BeautifulSoup as bs

from medios.diarios.diario import Diario
from medios.diarios.noticia import Noticia

from bd.entidades import Kiosco

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self, "clarin")

    def limpiar_texto(self, texto):
        regexp = re.compile(r'[\n\s]Newsletters[^\n]+\n')
        return re.sub(regexp,'',texto)

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    def limpiar_texto(self, texto):
        texto = texto.replace('SEGUIR', '')
        regexp = re.compile(r'[\n\s]Crédito[^\n]+\n')
        texto = re.sub(regexp,'',texto)
        regexp = re.compile(r'[\n\s]Comentar[^\n]+\n')
        return re.sub(regexp,'',texto)

    def parsear_fecha(self, entrada):
        return dateutil.parser.parse(entrada.updated)

class Infobae(Diario):

    def __init__(self):
        Diario.__init__(self, "infobae")

    def leer(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        tag_regexp = re.compile(r'<[^>]+>')
        for tag, url_feed in self.feeds.items():
            for entrada in fp.parse(url_feed).entries:
                titulo = entrada.title
                texto = re.sub(tag_regexp,'',entrada.content[0].value)
                fecha = dateutil.parser.parse(entrada.published)  - datetime.timedelta(hours=3)
                url = entrada.link
                if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                    continue
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

class CasaRosada(Diario):

    def __init__(self):
        Diario.__init__(self, "casarosada")

    def leer_todo(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        tag_regexp = re.compile(r'<[^>]+>')
        primer_linea_regexp = re.compile(r'^[^\n]+\n')

        entradas = []
        url_feed_template = self.feeds['todo'] + "&start="
        index = 0
        feed = fp.parse(url_feed_template + str(index))
        while len(feed.entries) > 0:
            entradas.extend(feed.entries)
            index += 40
            feed = fp.parse(url_feed_template + str(index))

        for entrada in entradas:
            titulo = entrada.title
            texto = bs(re.sub(tag_regexp,'',entrada.summary), features="lxml").text
            texto_limpio = re.sub(primer_linea_regexp,'',texto)
            if len(texto_limpio) == 0:
                texto_limpio = texto
                
            fecha = dateutil.parser.parse(entrada.published)
            url = entrada.link
            if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                continue
            self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria='todo', titulo=titulo, texto=texto_limpio))


    def leer(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        tag_regexp = re.compile(r'<[^>]+>')
        primer_linea_regexp = re.compile(r'^[^\n]+\n')

        for tag, url_feed in self.feeds.items():
            feed = fp.parse(url_feed)
            for entrada in feed.entries:
                titulo = entrada.title
                texto = bs(re.sub(tag_regexp,'',entrada.summary), features="lxml").text
                texto_limpio = re.sub(primer_linea_regexp,'',texto)
                if len(texto_limpio) == 0:
                    texto_limpio = texto

                fecha = dateutil.parser.parse(entrada.published)
                url = entrada.link
                if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                    continue
                self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=tag, titulo=titulo, texto=texto_limpio))
        