import yaml

class Fecha:
    def __init__(self, fecha=None):
        self.fecha = fecha

        with open("medios/diarios/config.yaml", 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        config_diario = config[self.etiqueta]
        for feed in config_diario["feeds"]:
            self.feeds[feed["tag"]] = feed["url"]    

        self.diarios = {}

    # 'noticias' deben ser json de tipo: { 'titulo' : "un_titulo", 'texto' : "un_texto", 'url' : "https://una.url.com/noticia" }
    def agregar(self, diario, categoria, noticias):

        urls = self.diarios[diario][categoria]['urls']
        noticias = [noticia for noticia in noticias if noticia['url'] not in urls]

        # agrego noticias
        self.diarios[diario][categoria].append(noticias)

        # agrego urls nuevas
        urls = [noticia['url'] for noticia in noticias]
        self.diarios[diario][categoria]['urls'].append(urls)

    def guardar(self):
        pass
    
    def recuperar(self):
        pass