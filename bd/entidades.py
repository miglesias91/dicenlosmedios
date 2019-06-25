import datetime
import dateutil

import yaml

import pymongo
from pymongo import MongoClient

class Kiosco:
    def __init__(self, fecha=None):
        self.fecha = ""
        self.fecha = fecha
        self.diarios = {}

        with open("medios/diarios/config.yaml", 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        for diario in config["diarios"]:
            nombre_diario = diario['tag']
            self.diarios[nombre_diario] = {}
            for feed in diario['feeds']:
                categoria_feed = feed['tag']
                self.diarios[nombre_diario][categoria_feed] = { "urls" : [], "noticias" : [] }

    def agregar(self, diario):
        for categoria, noticias in diario.categorias.items():
            json_noticias = [{ 'titulo' : noticia.titulo, 'texto' : noticia.texto, 'url' : noticia.url } for noticia in noticias]
            self.agregar_noticias(diario.etiqueta, categoria, json_noticias)

    # 'noticias' deben ser json de tipo: { 'titulo' : "un_titulo", 'texto' : "un_texto", 'url' : "https://una.url.com/noticia" }
    def agregar_noticias(self, diario, categoria, noticias):

        urls = self.diarios[diario][categoria]['urls']
        noticias = [noticia for noticia in noticias if noticia['url'] not in urls]

        # agrego noticias
        self.diarios[diario][categoria]['noticias'].extend(noticias)

        # agrego urls nuevas
        urls = [noticia['url'] for noticia in noticias]
        self.diarios[diario][categoria]['urls'].extend(urls)

        return len(urls)

    def guardar(self):
        
        cliente = MongoClient()

        bd = cliente.dlm

        if bd.fechas.find({"fecha":self.fecha}).count() > 0:
            return False

        return bd.fechas.insert_one({ "fecha" : self.fecha, "diarios" : self.diarios})
    
    def recuperar(self):
        cliente = MongoClient()

        bd = cliente.dlm

        fecha = bd.fechas.find_one({"fecha" : self.fecha })
        
        if fecha == None:
            return False
        
        self.diarios = fecha['diarios']
        return True

    def noticias(self, diario):
        noticias = []
        for categoria, urls_y_noticias in self.diarios[diario].items():
            noticias.extend(urls_y_noticias['noticias'])

        return noticias
