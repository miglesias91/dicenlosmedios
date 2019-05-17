from medios.medio import Medio

class Portal(Medio):

    def __init__(self):
        Medio.__init__(self)
        self.noticias = []
        self.periodistas = {}

    def actualizar_contenido(self):
        raise NotImplementedError()