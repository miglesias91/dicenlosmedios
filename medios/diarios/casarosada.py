import dateutil
import datetime
import yaml
import feedparser as fp
import newspaper as np
import re

import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

from medios.medio import Medio
from medios.diarios.noticia import Noticia
from medios.diarios.diario import Diario

from bd.entidades import Kiosco

class CasaRosada(Diario):

    def __init__(self):
        Diario.__init__(self, "casarosada")

    def leer_historico(self):
        with open('medios/diarios/config.yaml', 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        url_historica = ""
        for diario in config['diarios']:
            if diario['tag'] == self.etiqueta:
                url_historica = diario['feed_historico']
                break

        entradas = []
        url_historica = url_historica + "&start="
        index = 0
        feed = fp.parse(url_historica + str(index))
        intentos = 0
        while feed.bozo == 1 and intentos < 5:
            feed = fp.parse(url_historica + str(index))
            intentos += 1

        while len(feed.entries) > 0:
            entradas.extend(feed.entries)
            index += 40
            feed = fp.parse(url_historica + str(index))
            intentos = 0
            while feed.bozo == 1 and intentos < 5:
                feed = fp.parse(url_historica + str(index))
                intentos += 1      

        # TERMINAR DE ARMAR ESTO !!!!
        entradas = self.parsear_entradas()

        urls_discursos = self.parsear_urls_discursos(entradas)

        discursos = self.parsear_discursos(urls_discursos)

        discursos = []
        for entrada in entradas:
            titulo = entrada.title
            feed = bs(urllib.request.urlopen(entrada.link).read(), 'html.parser')
            elemento = feed.find(name='div', attrs={'class':'discurso btn btn-primary'})


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


    def parsear_entradas(self):
        pass

    def parsear_url_discursos(self, entradas):
        pass

    def parsear_discursos(self, urls_discursos):
        pass