import yaml

from medios.medio import Medio

class Diario(Medio):

    def __init__(self, etiqueta):
        Medio.__init__(self, etiqueta)
        self.noticias = []
        self.periodistas = {}
        self.categorias = {}
        self.feeds = {}
        self.configurar(self.etiqueta)

    def configurar(self, etiqueta):
        with open("medios/diarios/config.yaml", 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        config_diario = config[self.etiqueta]
        for feed in config_diario["feeds"]:
            self.feeds[feed["tag"]] = feed["url"]         

    def leer(self):
        raise NotImplementedError()

    def nueva_noticia(self, titulo, descripcion, texto, palabras_claves, imagen_url):
        raise NotImplementedError()