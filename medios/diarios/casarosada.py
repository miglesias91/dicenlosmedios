import dateutil
import datetime
import yaml
import feedparser as fp
import newspaper as np
import re

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

from medios.medio import Medio
from medios.diarios.noticia import Noticia
from medios.diarios.diario import Diario

from bd.entidades import Kiosco

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