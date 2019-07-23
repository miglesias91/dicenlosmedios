import dateutil
import datetime
import yaml
import feedparser as fp
import newspaper as np
import re
import string

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

from medios.medio import Medio
from medios.diarios.noticia import Noticia
from medios.diarios.diario import Diario

from bd.entidades import Kiosco

class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self, "paginadoce")
                    
    def leer(self):
        kiosco = Kiosco()

        print("leyendo '" + self.etiqueta + "'...")

        for url, fecha in self.entradas_feed():
            if kiosco.contar_noticias(diario=self.etiqueta, url=url): # si existe ya la noticia (url), no la decargo
                continue
            categoria, titulo, texto = self.parsear_noticia(url=url)
            if texto == None:
                continue
            self.noticias.append(Noticia(fecha=fecha, url=url, diario=self.etiqueta, categoria=categoria, titulo=titulo, texto=texto))

    def entradas_feed(self):
        urls_fechas = []
        req = Request(self.feed_noticias, headers={'User-Agent': 'Mozilla/5.0'})
        feed = bs(urlopen(req).read(), 'html.parser')
        for entrada in feed.find_all('url'):
            url = entrada.loc.string
            fecha = dateutil.parser.parse(entrada.find('news:publication_date').string)
            urls_fechas.append((url, fecha))
            
        return urls_fechas

    def parsear_noticia(self, url):
        articulo = np.Article(url=url, language='es')
        try:
            articulo.download()
            articulo.parse()
        except:
            return None
        
        signos = string.punctuation + "¡¿\n"
        categoria = articulo.meta_keywords[0].translate(str.maketrans('áéíóúý', 'aeiouy', signos)).strip().lower()

        if categoria == "el pais":
            categoria = "politica"

        if categoria == "el mundo":
            categoria = "internacional"

        return  categoria, articulo.title, articulo.text