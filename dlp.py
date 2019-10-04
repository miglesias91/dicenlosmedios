import getopt, sys
import time
import json
import datetime
from collections import defaultdict
import yaml
import pathlib
from  joblib import Parallel, delayed
import multiprocessing

import tweepy
from wordcloud import WordCloud as wc

import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from medios.diarios.clarin import Clarin
from medios.diarios.lanacion import LaNacion
from medios.diarios.eldestape import ElDestape
from medios.diarios.paginadoce import PaginaDoce
from medios.diarios.infobae import Infobae
from medios.diarios.telam import Telam
from medios.diarios.perfil import Perfil
from medios.diarios.ambito import Ambito
from medios.diarios.tn import TN
from medios.diarios.casarosada import CasaRosada

from ia import txt
from ia.txt import NLP
from bd.entidades import Kiosco
import utiles

def twittear_hilo(parametros):
    tw_intro = {'texto': "Análisis de discurso del string_fecha de #MauricioMacri.", 'media': ['intro0.png','intro1.png']}
    tw_terminos = { 'texto': 'tweet con terminos', 'media': ["dlp_terminos.png"] }
    tw_verbos = {'texto': 'tweet con verbos', 'media': ["dlp_verbos.png"]}

    utiles.twittear_hilo([tw_intro, tw_terminos, tw_verbos])
    return 
    fecha = parametros['fecha']

    kiosco = Kiosco()
    textos = [noticia['texto'] for noticia in kiosco.noticias(diario='casarosada', categorias='', fecha=fecha)]

    if len(textos) == 0:
        return

    nlp = NLP()
    nlp.separador = ''
    
    for texto in textos:
        string_fecha = ""
        if type(fecha) is dict:
            string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
        else:
            string_fecha = fecha.strftime("%d.%m.%Y")

        tw_intro = tweet_intro(texto, string_fecha)

        kiosco = Kiosco()

        top_terminos = nlp.top_terminos(textos=[texto])
        top_verbos = nlp.top_verbos(textos=[texto])

        tw_terminos = tweet_terminos(top_terminos)
        tw_verbos = tweet_verbos(top_verbos)

        if parametros['twittear']:
            utiles.twittear_hilo([tw_intro, tw_terminos, tw_verbos])

def tweet_intro(texto, string_fecha):
    font = 'calibri.ttf'
    paths_imagenes = utiles.texto_en_imagenes(texto, font, 15, 800, 600, "intro")

    return {'texto': "Análisis de discurso del " + string_fecha + " de #MauricioMacri.", 'media': paths_imagenes}

def tweet_terminos(top_terminos):
    texto = "Verbos tendencia:\n"

    i = 0
    for nombre, m in top_terminos:
        linea = ""
        i += 1
        if i >= 10:
            linea = str(i) + ". #" + nombre + " " + str(m) + "\n"
            texto += linea
            break
        else:
            linea = str(i) + ".  #" + nombre + " " + str(m) + "\n"

        if len(texto) + len(linea) > 220:
            break
        else:
            texto += linea

    print(texto)

    return {'texto': texto, 'media': ["dlp_terminos.png"]}

def tweet_verbos(top_verbos):
    texto = "Terminos tendencia:\n"

    i = 0
    for nombre, m in top_verbos:
        linea = ""
        i += 1
        if i >= 10:
            linea = str(i) + ". #" + nombre + " " + str(m) + "\n"
            texto += linea
            break
        else:
            linea = str(i) + ".  #" + nombre + " " + str(m) + "\n"

        if len(texto) + len(linea) > 220:
            break
        else:
            texto += linea

    print(texto)

    return {'texto': texto, 'media': ["dlp_verbos.png"]}

def usage(parametros):
    print("dlp (dicen-los-presidentes) v1.1")
    print("ACCIONES")
    print("PARAMETROS OPCIONALES")
    print("--fecha AAAAMMDD - analiza las noticias con fecha AAAMMDD")
    print("--fecha AAAAMMDD-AAAAMMDD - analiza las noticias dentro del rango de fechas AAAAMMDD->AAAAMMDD")
    print("--twittear - indica que el texto y la imagén resultante se suben a @dicenlosmedios")

def main():
    accion = None
    top_max = 10
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "fecha=", "twittear"])
    except getopt.GetoptError as err:
        print(err)
        usage(None)
        sys.exit(2)

    parametros = {'fecha':datetime.datetime.now().date(), 'twittear':False}
    accion = twittear_hilo
    for o, a in opts:
        if o == "--help" or o == "-h":
            accion=usage
        elif o == "--fecha":
            fecha = None
            if len(a.split('-')) == 2:
                desde = datetime.datetime.strptime(a.split('-')[0], "%Y%m%d")
                desde.replace(hour=0, minute=0, second=0)
                hasta = datetime.datetime.strptime(a.split('-')[1], "%Y%m%d")
                hasta.replace(hour=23, minute=59, second=59)
                fecha = {'desde':desde, 'hasta':hasta}
            else:
                fecha = datetime.datetime.strptime(a, "%Y%m%d")

            parametros['fecha'] = fecha
        elif o == "--twittear":
            parametros['twittear'] = True
        else:
            assert False, "opción desconocida"
    
    # ejecuto accion con sus parametros
    accion(parametros)

if __name__ == "__main__":
    main()