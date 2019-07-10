import getopt, sys
import time
import json
import datetime
from collections import defaultdict
import yaml
import pathlib

import tweepy
from wordcloud import WordCloud as wc

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce, CasaRosada
from ia import txt
from ia.txt import NLP, freq
from bd.entidades import Kiosco

def leer_medios(parametros):
    medios = set(parametros['medios'])

    kiosco = Kiosco()


    # infobae.com
    infobae = Infobae()
    if infobae.etiqueta in medios:
        infobae.leer()
        kiosco.actualizar_diario(infobae)

    # clarin.com
    clarin = Clarin()
    if clarin.etiqueta in medios:
        clarin.leer()
        kiosco.actualizar_diario(clarin)

    # lanacion.com
    lanacion = LaNacion()
    if lanacion.etiqueta in medios:
        lanacion.leer()
        kiosco.actualizar_diario(lanacion)

    # eldestapeweb.com
    eldestape = ElDestape()
    if eldestape.etiqueta in medios:
        eldestape.leer()
        kiosco.actualizar_diario(eldestape)

    # pagina12.com
    p12 = PaginaDoce()
    if p12.etiqueta in medios:
        p12.leer()
        kiosco.actualizar_diario(p12)

    # casarosada.com
    casarosada = CasaRosada()
    if casarosada.etiqueta in medios:
        casarosada.leer()
        kiosco.actualizar_diario(casarosada)

def top(parametros):
    fecha = parametros['fecha']
    top_max = parametros['top_max']
    medios = set(parametros['medios'])

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
    
        textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue

        texto = "Top " +  str(top_max) + " palabras más frecuentes en las noticias de " + twitter + " del " + fecha.strftime("%d.%m.%Y") + "\n"

        top_100 = nlp.top(textos, n=100)

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

            if len(texto) + len(linea) < 220:
                texto += linea
            else:
                break

        print(texto)

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
        wordcloud = wc(font_path='C:\Windows\Fonts\consola.ttf',width=1280,height=720,background_color="black",colormap='Blues',min_font_size=14,prefer_horizontal=1,relative_scaling=1).generate_from_frequencies(dic_top_100)
        wordcloud.recolor(100)
        path_imagen = tag + ".png"
        wordcloud.to_file(path_imagen)
        api.update_with_media(filename=path_imagen, status=texto)

def top_personas(parametros):
 #¡¡¡¡¡¡¡¡¡¡ MEJORAR RESULTADOS !!!!!!!!!!!!!!!    
    fecha = parametros['fecha']
    top_max = parametros['top_max']
    medios = set(parametros['medios'])

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
    
        textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue

        texto = "Top " + str(top_max)  + " personas más frecuentes en las noticias de " + twitter + " del " + fecha.strftime("%d.%m.%Y") + "\n"

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

            if len(texto) + len(linea) < 220:
                texto += linea
            else:
                break

        print(texto)

# leer_diarios()

# subir_top_diez(string_fecha="20190704")

# subir_top_personas(string_fecha="20190705")

def usage():
    print("dlm (dicen-los-medios) v1.1")
    print("ACCIONES")
    print("--leer [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - actualiza las noticias de todos los diarios, a menos que se especifiquen los MEDIOS en particular")
    print("--top [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de palabras de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("--top-personas [MAX] [MEDIO_1] [MEDIO_2] ... [MEDIO_N] - muestra el top MAX de personas de todos los medios, a menos que se especifiquen los MEDIOS a analizar")
    print("PARAMETROS OPCIONALES")
    print("--fecha AAAAMMDD - selecciona las noticias con fecha AAAMMDD")
    print("--fecha AAAAMMDD_desde-AAAAMMDD_hasta - selecciona las noticias dentro del  rango de fechas AAAAMMDD_desde -> AAAAMMDD_hasta ")
    print("--twittear - indica que el texto y la imagén resultante se suben a @dicenlosmedios")

def main():
    accion = None
    twittear = False
    fecha = datetime.datetime.now().date()
    top_max = 10
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "leer", "top=", "top-personas=", "fecha=", "twittear"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    medios = args

    parametros = {'medios':medios}
    for o, a in opts:
        if o == "--help" or o == "-h":
            usage()
        elif o == "--leer":
            accion=leer_medios
        elif o == "--top":
            if a:
                top_max = a
            parametros['top_max'] = top_max
            accion=top
        elif o == "--top-personas":
            if a:
                top_max = a
            parametros['top_max'] = top_max
            accion=top_personas
        elif o == "--fecha":
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
            twittear = True
        else:
            assert False, "opción desconocida"
    
    # ejecuto accion con sus parametros
    accion(parametros)

if __name__ == "__main__":
    main()