from medios.medio import Medio

class Diario(Medio):

    def __init__(self):
        Medio.__init__(self)
        self.noticias = []
        self.periodistas = {}
        self.categorias = {}

    def leer(self):
        raise NotImplementedError()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        raise NotImplementedError()