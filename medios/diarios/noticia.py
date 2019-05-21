from medios.contenido import Contenido

class Noticia(Contenido):

    def __init__(self):
        Contenido.__init__(self)
        self.texto = ""
        self.imagen = ""
        self.tags = []
        self.autor = 0
        self.palabras_claves = []
        self.fecha = ""
