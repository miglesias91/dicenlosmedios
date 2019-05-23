from medios.contenido import Contenido

class Noticia(Contenido):

    def __init__(self, titulo, texto, url_imagen, tags, autor, palabras_claves, fecha):
        Contenido.__init__(self)
        self.titulo = titulo
        self.texto = texto
        self.url_imagen = url_imagen
        self.tags = tags
        self.autor = autor
        self.palabras_claves = palabras_claves
        self.fecha = fecha
