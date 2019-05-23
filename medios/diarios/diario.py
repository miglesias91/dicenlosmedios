import yaml

from medios.medio import Medio

class Diario(Medio):

    def __init__(self, etiqueta):
        Medio.__init__(self, etiqueta)
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
        for tag, url_feed in self.feeds.items():
            for url_noticia in self.reconocer_urls_noticias(url_feed=url_feed):
                noticia = self.nueva_noticia(url=url_noticia)
                self.categorias[tag].append(noticia)

    def reconocer_urls_noticias(self, url_feed):
        raise NotImplementedError()

    def nueva_noticia(self, url):
        raise NotImplementedError()