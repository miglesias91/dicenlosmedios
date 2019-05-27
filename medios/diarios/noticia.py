from medios.contenido import Contenido

class Noticia(Contenido):

    def __init__(self, titulo, texto, fecha, url):
        Contenido.__init__(self)
        self.titulo = titulo
        self.texto = texto
        self.fecha = fecha
        self.url = url
