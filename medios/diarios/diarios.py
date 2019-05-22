from medios.diarios.diario import Diario
import feedparser as fp
import newspaper as np

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self, "clarin")

    def leer(self):

        for tag, url in self.feeds.items():
            entradas = fp.parse(url)
            for entrada in entradas.entries:
                art = np.Article(url=entrada.link, language='es')
                art.download()
                art.parse()
                art.nlp()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self, "lanacion")

    def leer(self):
        for tag, url in self.feeds.items():
            entradas = fp.parse(url)
            for entrada in entradas.entries:
                art = np.Article(url=entrada.link, language='es')
                art.download()
                art.parse()
                art.nlp()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class Infobae(Diario):

    def __init__(self):
        Diario.__init__(self, "infobae")

    def leer(self):
        pass

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self, "paginadoce")

    def leer(self):
        for tag, url in self.feeds.items():
            entradas = fp.parse(url)
            for entrada in entradas.entries:
                art = np.Article(url=entrada.link, language='es')
                art.download()
                art.parse()
                art.nlp()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass

class ElDestape(Diario):

    def __init__(self):
        Diario.__init__(self, "eldestape")
        
    def leer(self):
        for tag, url in self.feeds.items():
            entradas = fp.parse(url)
            for entrada in entradas.entries:
                art = np.Article(url=entrada.link, language='es')
                art.download()
                art.parse()
                art.nlp()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        pass