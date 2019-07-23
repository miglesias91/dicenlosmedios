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
                if kiosco.contar_noticias(diario=self.etiqueta, url=url): # si existe ya la noticia (url), no la decargo
                    continue
                self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=tag, titulo=titulo, texto=self.limpiar_texto(texto)))