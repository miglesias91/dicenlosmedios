import dateutil
import datetime
import re
import feedparser as fp
import urllib.request
from bs4 import BeautifulSoup as bs
import newspaper as np

from medios.diarios.diario import Diario
from medios.diarios.noticia import Noticia

from bd.entidades import Kiosco

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self, "clarin")

    def limpiar_texto(self, texto):
        regexp = re.compile(r'[\n\s]Newsletters[^\n]+\n')
        texto = re.sub(regexp,' ',texto)
        regexp = re.compile(r'[\n\s]Mirá también[^\n]+\n')
        return re.sub(regexp,' ',texto)

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    def limpiar_texto(self, texto):
        texto = texto.replace('SEGUIR', '')
        regexp = re.compile(r'[\n\s]Crédito[^\n]+\n')
        texto = re.sub(regexp,' ',texto)
        regexp = re.compile(r'[\n\s]Comentar[^\n]+\n')
        texto = re.sub(regexp,' ',texto)
        regexp = re.compile(r'[\n\s]Fuente[^\n]+\n')
        texto = re.sub(regexp,' ',texto)
        regexp = re.compile(r'[\n\s]Crédito[^\n]+\n')
        return re.sub(regexp,' ',texto)

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
                texto = re.sub(tag_regexp,' ',entrada.content[0].value)
                fecha = dateutil.parser.parse(entrada.published)  - datetime.timedelta(hours=3)
                url = entrada.link
                if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                    continue
                self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=tag, titulo=titulo, texto=self.limpiar_texto(texto)))

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

    def nueva_noticia(self, url, categoria, diario):
        articulo = np.Article(url=url, language='es')
        try:
            articulo.download()
            articulo.parse()
        except:
            return None

        categoria_parseada = self.reconocer_categoria(articulo.html)
        if len(categoria_parseada) != 0:
            categoria = categoria_parseada

        return Noticia(fecha=articulo.publish_date, url=url, diario=diario, categoria=categoria, titulo=articulo.title, texto=self.limpiar_texto(articulo.text))

    def reconocer_urls_y_fechas_noticias(self, url_feed):
        urls_y_fechas = []
        feed = bs(urllib.request.urlopen(url_feed).read(), 'html.parser')
        for elemento_url in feed.find_all('url'):
            url = elemento_url.loc.string
            fecha = dateutil.parser.parse(elemento_url.find('news:publication_date').string) - datetime.timedelta(hours=3)
            urls_y_fechas.append((url, fecha))
        return urls_y_fechas

    def reconocer_categoria(self, raw_html):
        feed = bs(raw_html, 'html.parser')
        elemento = feed.find(name='div', attrs={'class':'category-wrapper'})
        return elemento.next_element.replace('\n', '').strip().lower()

    def limpiar_texto(self, texto):
        regexp = re.compile(r'[\n\s]LEA MÁS[^\n]+\n')
        return re.sub(regexp,' ',texto)

class CasaRosada(Diario):

    def __init__(self):
        Diario.__init__(self, "casarosada")

    def leer_todo(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        tag_regexp = re.compile(r'<[^>]+>')

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
            texto = bs(re.sub(tag_regexp,' ',entrada.summary), features="lxml").text
                
            fecha = dateutil.parser.parse(entrada.published)
            url = entrada.link
            if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                continue
            self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria='todo', titulo=titulo, texto=self.limpiar_texto(texto)))


    def leer(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        tag_regexp = re.compile(r'<[^>]+>')

        for tag, url_feed in self.feeds.items():
            feed = fp.parse(url_feed)
            for entrada in feed.entries:
                titulo = entrada.title
                texto = bs(re.sub(tag_regexp,' ',entrada.summary), features="lxml").text

                fecha = dateutil.parser.parse(entrada.published)
                url = entrada.link
                if kiosco.bd.noticias.find(filter={'diario':self.etiqueta, 'url':url}).count() > 0: # si existe ya la noticia (url), no la decargo
                    continue
                self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=tag, titulo=titulo, texto=self.limpiar_texto(texto)))

    def limpiar_texto(self, texto):
        primer_linea_regexp = re.compile(r'^[^\n]+\n')
        texto_limpio = re.sub(primer_linea_regexp,' ',texto)
        if len(texto_limpio) == 0:
            texto_limpio = texto
        return texto_limpio
