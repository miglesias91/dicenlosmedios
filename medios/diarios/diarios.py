import yaml

from medios.diarios.diario import Diario

class Clarin(Diario):

    def __init__(self):
        Diario.__init__(self)
        self.feeds = {}

        with open("config.yaml", 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # etiqueta = "clarin"
        # config_diario = config[etiqueta]
        # self.feeds[]

    


class LaNacion(Diario):

    def __init__(self):
        Diario.__init__(self)
        self.feeds = {}


class Infobae(Diario):

    def __init__(self):
        Diario.__init__(self)
        self.feeds = {}


class PaginaDoce(Diario):

    def __init__(self):
        Diario.__init__(self)
        self.feeds = {}


class ElDestape(Diario):

    def __init__(self):
        Diario.__init__(self)
        self.feeds = {}