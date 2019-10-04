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

        hashtag = diario['hashtag']
    
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

        categorias = ["#"+c for c in categorias]

        secciones = ""
        if len(categorias) > 0:
            secciones = " de " + " y ".join([", ".join(categorias[:-1]),categorias[-1]] if len(categorias) > 2 else categorias)

        texto = "Tendencias en " + contenido + secciones + " de " + hashtag + " del " + string_fecha + "\n"

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

            path_imagen = tag + ".png"
            utiles.nube_de_palabras(path=path_imagen, data=dict(top_todo))
            utiles.twittear(texto=texto, path_imagen=path_imagen)


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

def top_verbos(parametros):
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

        top_100 = nlp.top_verbos(textos, n=top_max)

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
        if total == 0:
            continue
        for cat in categorias:
            n = k.contar_noticias(diario=tag, categorias=[cat], fecha=fecha)
            lista_medio.append(n)
        data.append([n*100/total for n in lista_medio])

    conteo = np.array(data)

    fig, ax = plt.subplots()

    im, cbar = utiles.heatmap(conteo, etiqueta_medios, categorias, ax=ax, cmap=utiles.cmap_del_dia(), cbarlabel=string_fecha, cbar_format="{x:.0f}%")
    texts = utiles.annotate_heatmap(im, valfmt="{x:.1f}")

    path_imagen = "intensidad.jpg"

    fig.tight_layout()
    plt.savefig(path_imagen, bbox_inches='tight',dpi=100)

    if len(categorias) > 0:
        hashtags_categorias = " #" + " #".join([" #".join(categorias[:-1]),categorias[-1]] if len(categorias) > 2 else categorias)

    medios = list(medios)
    if len(medios) > 0:
        hashtags_medios = " #" + " #".join([" #".join(medios[:-1]),medios[-1]] if len(medios) > 2 else medios)

    if twittear:
        texto = "Porcentaje de noticias x categoría." + hashtags_medios + hashtags_categorias + "."
        utiles.twittear(texto=texto, path_imagen=path_imagen) 

def perfil(parametros):
    fecha = parametros['fecha']
    medios = set(parametros['medios'])
    twittear = parametros['twittear']

    if len(medios) == 0:
        medios = set(['clarin', 'lanacion', 'infobae', 'paginadoce', 'eldestape', 'telam', 'perfil', 'ambito', 'tn'])

    string_fecha = ""
    if type(fecha) is dict:
        string_fecha = fecha['desde'].strftime("%d.%m.%Y") + " al " + fecha['hasta'].strftime("%d.%m.%Y")
    else:
        string_fecha = fecha.strftime("%d.%m.%Y")

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    etiqueta_medios = []
    k = Kiosco()
    for diario in config['diarios']:
        tag = diario['tag']
        categorias = k.categorias_existentes(diario=tag)
        etiqueta_medios = [diario['twitter']]
        if tag not in medios:
            continue
        lista_medio = []
        total = k.contar_noticias(diario=tag, fecha=fecha)
        if total == 0:
            continue
        for cat in categorias:
            n = k.contar_noticias(diario=tag, categorias=[cat], fecha=fecha)
            lista_medio.append(n)

        data = []
        data.extend([n*100/total for n in lista_medio])

        path_imagen = "perfil-" + tag + ".jpg"
        utiles.lollipop(path=path_imagen, colormap=utiles.cmap_del_dia(), titulo="Resumen de " + diario['twitter'] + " - " + string_fecha, etiquetas=categorias, unidad="cantidad de noticias", valfmt="{x:.0f}", data=lista_medio)

        if twittear:
            texto = "Suma de noticias de #" + tag + " del " + string_fecha + ", en cada una de sus secciones."
            utiles.twittear(texto=texto, path_imagen=path_imagen)

def usage(parametros):
    print("dlm (dicen-los-medios) v1.1")
    print("ACCIONES")
    print("--leer [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - actualiza las noticias de todos los diarios, a menos que se especifiquen los MEDIOS en particular")
    print("--top-todo [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de terminos, palabras, etc, etct, de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-terminos [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de terminos de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-personas [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de personas de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-verbos [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de verbos de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--intensidad [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra una tabla con la intensidad de noticias por categorias de todos los medios, a menos que se especifiquen los MEDIOS a incluir en la tabla")
    print("--perfil [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra la cantidad de noticias por categoria de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("PARAMETROS OPCIONALES")
    print("--categorias c1-c2-...-cn - analiza las noticias de las categorias c1, c2, ..., cn: CATEGORIAS DISPONIBLES: 'politica', 'economia', 'sociedad', 'internacional', 'cultura', 'espectaculos', 'deportes'")
    print("--fecha AAAAMMDD - analiza las noticias con fecha AAAMMDD")
    print("--fecha AAAAMMDD-AAAAMMDD - analiza las noticias dentro del rango de fechas AAAAMMDD->AAAAMMDD")
    print("--twittear - indica que el texto y la imagén resultante se suben a @dicenlosmedios")
    print("--solo-titulos - indica que solo se analizan títulos")

def main():
    accion = None
    top_max = 10
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "leer", "top-todo=", "top-terminos=", "top-personas=", "top-verbos=", "intensidad", "perfil", "fecha=", "categorias=", "twittear", "solo-titulos"])
    except getopt.GetoptError as err:
        print(err)
        usage(None)
        sys.exit(2)

    parametros = {'medios':args, 'fecha':datetime.datetime.now().date(), 'twittear':False, 'solo_titulos':False, 'categorias':''}
    for o, a in opts:
        if o == "--help" or o == "-h":
            accion=usage
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
        elif o == "--top-verbos":
            try:
                top_max = int(a)
            except ValueError:
                pass
            parametros['top_max'] = top_max
            accion=top_verbos
        elif o == "--intensidad":
            accion=intensidad
        elif o == "--perfil":
            accion=perfil
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