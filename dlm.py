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

# from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce, CasaRosada
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

def leer_medio(medio):
    medio.leer()

    kiosco = Kiosco()
    kiosco.actualizar_diario(medio)

def leer_medios(parametros):
    medios_a_leer = set(parametros['medios'])

    medios = [Clarin(), LaNacion(), ElDestape(), PaginaDoce(), Infobae(), Telam(), Perfil(), Ambito(), TN(), CasaRosada()]

    num_cores = multiprocessing.cpu_count()
    Parallel(prefer="threads",n_jobs=num_cores)(delayed(leer_medio)(medio) for medio in medios if medio.etiqueta in medios_a_leer or len(medios_a_leer) == 0)

def top_todo(parametros):
    fecha = parametros['fecha']
    top_max = parametros['top_max']
    medios = set(parametros['medios'])
    categorias = parametros['categorias']
    twittear = parametros['twittear']
    solo_titulos = parametros['solo_titulos']

    kiosco = Kiosco()

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nlp = NLP()
    nlp.separador = ''
    for diario in config['diarios']:
        tag = diario['tag']
        if tag not in medios and len(medios) > 0:
            continue

        twitter = diario['twitter']
    
        textos = []
        contenido = "las noticias"
        if solo_titulos:
            textos = [noticia['titulo'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]            
            contenido = "los títulos"
        else:
            textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue
        
        string_fecha = ""
        if type(fecha) is dict:
            string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
        else:
            string_fecha = fecha.strftime("%d.%m.%Y")

        texto = "Tendencias en " + contenido +" de " + twitter + " del " + string_fecha + "\n"

        top_todo = nlp.top(textos, n=top_max)
        i = 0
        for nombre, m in top_todo:
            linea = ""
            i += 1
            if i >= 10:
                linea = str(i) + ". #" + nombre + " " + str(m) + "\n"
                texto += linea
                break
            else:
                linea = str(i) + ".  #" + nombre + " " + str(m) + "\n"

            if twittear and len(texto) + len(linea) > 220:
                break
            else:
                texto += linea

        print(texto)

        if twittear:
            claves = open("twitter.keys", "r")
            json_claves = json.load(claves)

            consumer_key = json_claves['consumer_key']
            consumer_secret = json_claves['consumer_secret']
            access_token = json_claves['access_token']
            access_token_secret = json_claves['access_token_secret']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

            dic_top_100 = dict(top_todo)
            wordcloud = wc(font_path='C:\Windows\Fonts\consola.ttf',width=1280,height=720,background_color="black",colormap=utiles.cmap_del_dia(),min_font_size=14,prefer_horizontal=1,relative_scaling=1).generate_from_frequencies(dic_top_100)
            wordcloud.recolor(100)
            path_imagen = tag + ".png"
            wordcloud.to_file(path_imagen)
            api.update_with_media(filename=path_imagen, status=texto)

def top_terminos(parametros):
    fecha = parametros['fecha']
    top_max = parametros['top_max']
    medios = set(parametros['medios'])
    categorias = parametros['categorias']
    twittear = parametros['twittear']
    solo_titulos = parametros['solo_titulos']

    kiosco = Kiosco()

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nlp = NLP()
    for diario in config['diarios']:
        tag = diario['tag']

        if tag not in medios and len(medios) > 0:
            continue

        twitter = diario['twitter']
    
        textos = []
        contenido = "las noticias"
        if solo_titulos:
            textos = [noticia['titulo'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]            
            contenido = "los títulos"
        else:
            textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue

        string_fecha = ""
        if type(fecha) is dict:
            string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
        else:
            string_fecha = fecha.strftime("%d.%m.%Y")

        texto = "Tendencias en " + contenido + " de " + twitter + " del " + string_fecha + "\n"

        top_100 = nlp.top_terminos(textos, n=top_max)

        i = 0
        for nombre, m in top_100:
            linea = ""
            i += 1
            if i >= 10:
                linea = str(i) + ". #" + nombre + " " + str(m) + "\n"
                texto += linea
                break
            else:
                linea = str(i) + ".  #" + nombre + " " + str(m) + "\n"

            if twittear and len(texto) + len(linea) > 220:
                break
            else:
                texto += linea

        print(texto)

        if twittear:
            claves = open("twitter.keys", "r")
            json_claves = json.load(claves)

            consumer_key = json_claves['consumer_key']
            consumer_secret = json_claves['consumer_secret']
            access_token = json_claves['access_token']
            access_token_secret = json_claves['access_token_secret']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

            dic_top_100 = dict(top_100)
            wordcloud = wc(font_path='C:\Windows\Fonts\consola.ttf',width=1280,height=720,background_color="black",colormap=utiles.cmap_del_dia(),min_font_size=14,prefer_horizontal=1,relative_scaling=1).generate_from_frequencies(dic_top_100)
            wordcloud.recolor(100)
            path_imagen = tag + ".png"
            wordcloud.to_file(path_imagen)
            api.update_with_media(filename=path_imagen, status=texto)

def top_personas(parametros):
    fecha = parametros['fecha']
    top_max = parametros['top_max']
    medios = set(parametros['medios'])
    categorias = parametros['categorias']
    twittear = parametros['twittear']
    solo_titulos = parametros['solo_titulos']

    kiosco = Kiosco()

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nlp = NLP()
    for diario in config['diarios']:
        tag = diario['tag']
        if tag not in medios and len(medios) > 0:
            continue

        twitter = diario['twitter']
    
        textos = []
        contenido = "las noticias"
        if solo_titulos:
            textos = [noticia['titulo'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]            
            contenido = "los títulos"
        else:
            textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, categorias=categorias, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue
        
        string_fecha = ""
        if type(fecha) is dict:
            string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
        else:
            string_fecha = fecha.strftime("%d.%m.%Y")

        texto = "Tendencias en " + contenido + " de " + twitter + " del " + string_fecha + "\n"

        top_100 = nlp.top_personas(textos, n=top_max)

        i = 0
        for nombre, m in top_100:
            linea = ""
            i += 1
            if i >= 10:
                linea = str(i) + ". #" + nombre + " " + str(m) + "\n"
                texto += linea
                break
            else:
                linea = str(i) + ".  #" + nombre + " " + str(m) + "\n"

            if twittear and len(texto) + len(linea) > 220:
                break
            else:
                texto += linea

        print(texto)

def intensidad(parametros):
    fecha = parametros['fecha']
    medios = set(parametros['medios'])
    categorias = parametros['categorias']
    twittear = parametros['twittear']

    if len(categorias) == 0:
        categorias = ['politica', 'economia', 'sociedad', 'internacional', 'deportes', 'espectaculos', 'cultura']

    if len(medios) == 0:
        medios = set(['clarin', 'lanacion', 'infobae', 'paginadoce', 'eldestape', 'telam', 'perfil', 'ambito', 'tn'])

    string_fecha = ""
    if type(fecha) is dict:
        string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
    else:
        string_fecha = fecha.strftime("%d.%m.%Y")

    data = []
    k = Kiosco()

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    etiqueta_medios = []
    for diario in config['diarios']:
        tag = diario['tag']
        etiqueta_medios.append(diario['twitter'])
        if tag not in medios and len(medios) > 0:
            continue
        lista_medio = []
        total = k.contar_noticias(diario=tag, fecha=fecha)
        for cat in categorias:
            n = k.contar_noticias(diario=tag, categorias=[cat], fecha=fecha)
            lista_medio.append(n)
            total += n
        data.append([n*100/total for n in lista_medio])

    conteo = np.array(data)

    fig, ax = plt.subplots()

    im, cbar = utiles.heatmap(conteo, etiqueta_medios, categorias, ax=ax, cmap=utiles.cmap_del_dia(), cbarlabel=string_fecha)
    texts = utiles.annotate_heatmap(im, valfmt="{x:.1f}")

    fig.tight_layout()
    plt.show()

def usage():
    print("dlm (dicen-los-medios) v1.1")
    print("ACCIONES")
    print("--leer [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - actualiza las noticias de todos los diarios, a menos que se especifiquen los MEDIOS en particular")
    print("--top-todo [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de terminos, palabras, etc, etct, de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-terminos [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de terminos de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-personas [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de personas de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--intensidad [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra la intensidad de noticias de los medios segun la categoria")
    print("PARAMETROS OPCIONALES")
    print("--categorias c1-c2-...-cn - analiza las noticias de las categorias c1, c2, ..., cn: CATEGORIAS DISPONIBLES: 'politica', 'economia', 'sociedad', 'internacional', 'cultura', 'espectaculos', 'deportes'")
    print("--fecha AAAAMMDD - analiza las noticias con fecha AAAMMDD")
    print("--fecha AAAAMMDD_desde-AAAAMMDD_hasta - analiza las noticias dentro del rango de fechas AAAAMMDD_desde -> AAAAMMDD_hasta ")
    print("--twittear - indica que el texto y la imagén resultante se suben a @dicenlosmedios")
    print("--solo-titulos - indica que solo se analizan títulos")

def main():
    # heatmap()
    # return

    accion = None
    top_max = 10
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "leer", "top-todo=", "top-terminos=", "top-personas=", "intensidad", "fecha=", "categorias=", "twittear", "solo-titulos"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    parametros = {'medios':args, 'fecha':datetime.datetime.now().date(), 'twittear':False, 'solo_titulos':False, 'categorias':''}
    for o, a in opts:
        if o == "--help" or o == "-h":
            usage()
        elif o == "--leer":
            accion=leer_medios
        elif o == "--top-todo":
            try:
                top_max = int(a)
            except ValueError:
                pass
            parametros['top_max'] = top_max
            accion=top_todo
        elif o == "--top-terminos":
            try:
                top_max = int(a)
            except ValueError:
                pass
            parametros['top_max'] = top_max
            accion=top_terminos
        elif o == "--top-personas":
            try:
                top_max = int(a)
            except ValueError:
                pass
            parametros['top_max'] = top_max
            accion=top_personas
        elif o == "--intensidad":
            accion=intensidad
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

        elif o == "--categorias":
            parametros['categorias'] = a.split('-')

        elif o == "--twittear":
            parametros['twittear'] = True
        elif o == "--solo-titulos":
            parametros['solo_titulos'] = True
        else:
            assert False, "opción desconocida"
    
    # ejecuto accion con sus parametros
    accion(parametros)

if __name__ == "__main__":
    main()