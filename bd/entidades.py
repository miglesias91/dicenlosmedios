import datetime
import dateutil

import yaml

import pymongo
from pymongo import MongoClient

class Kiosco:
    def __init__(self, fecha=None):
        # self.fecha = ""
        # self.fecha = fecha
        # self.diarios = {}
        self.bd = MongoClient().dlm

        # with open("medios/diarios/config.yaml", 'r') as stream:
        #     try:
        #         config = yaml.safe_load(stream)
        #     except yaml.YAMLError as exc:
        #         print(exc)

        # for diario in config["diarios"]:
        #     nombre_diario = diario['tag']
        #     self.diarios[nombre_diario] = {}
        #     for feed in diario['feeds']:
        #         categoria_feed = feed['tag']
        #         self.diarios[nombre_diario][categoria_feed] = { "urls" : [], "noticias" : [] }

    def actualizar_diario(self, diario):
        urls = self.bd.noticias.find(filter={'diario':diario.etiqueta}, projection=['url'])
        json_noticias = [{'fecha':n.fecha, 'url':n.url, 'diario':n.diario, 'cat':n.categoria,'titulo':n.titulo, 'texto':n.texto} for n in diario.noticias if n.url not in urls]

        if len(json_noticias) == 0:
            print("no hay noticias nuevas de '" + diario.etiqueta + "'")
            return 0

        print("agregando " + str(len(json_noticias)) + " noticias nuevas de '" + diario.etiqueta + "'...")

        return self.bd.noticias.insert_many(json_noticias)

    def noticias(self, fecha=None, diario=None, categoria=None, fecha_in=True, url_in=True, diario_in=True, cat_in=True, tit_in=True, text_in=True):
        query = {}

        if fecha:
            query['fecha']=fecha

        if diario:
            query['diario']=diario

        if categoria:
            query['cat']=categoria

        projection = {'fecha':fecha_in, 'url':url_in, 'diario':diario_in, 'cat':cat_in, 'titulo':tit_in, 'texto':text_in }

        return self.bd.find(query, projection)

    def guardar_noticias(self, noticias):
        json_noticias = [{'fecha':n.fecha, 'url':n.url, 'diario':n.diario, 'cat':n.categoria,'titulo':n.titulo, 'texto':n.texto} for n in noticias]
        
        if len(json_noticias) == 0:
            return 0

        return self.bd.noticias.insert_many(json_noticias)

    def agregar(self, diario):

        json_noticias = [{'fecha':n.fecha.strftime("%Y%m%d"), 'url':n.url, 'diario':n.diario, 'cat':n.categoria,'titulo':n.titulo, 'texto':n.texto} for n in diario.noticias]
        
        if len(json_noticias) == 0:
            return 0
        
        cliente = MongoClient()
        bd = cliente.dlm

        return bd.noticias.insert_many(json_noticias)
        # for categoria, noticias in diario.categorias.items():
        #     json_noticias = [{ 'titulo' : noticia.titulo, 'texto' : noticia.texto, 'url' : noticia.url } for noticia in noticias]
        #     self.agregar_noticias(diario.etiqueta, categoria, json_noticias)

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
