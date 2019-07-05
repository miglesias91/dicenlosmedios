import getopt, sys
import time
import json
import datetime
from collections import defaultdict
import yaml
import pathlib

import tweepy
from wordcloud import WordCloud as wc

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce
from ia import txt
from ia.txt import NLP, freq
from bd.entidades import Kiosco

def leer_diarios():

    kiosco = Kiosco()

    # infobae.com
    infobae = Infobae()
    infobae.leer()
    kiosco.actualizar_diario(infobae)

    # clarin.com
    clarin = Clarin()
    clarin.leer()
    kiosco.actualizar_diario(clarin)

    # lanacion.com
    lanacion = LaNacion()
    lanacion.leer()
    kiosco.actualizar_diario(lanacion)

    # eldestapeweb.com
    eldestape = ElDestape()
    eldestape.leer()
    kiosco.actualizar_diario(eldestape)

    # pagina12.com
    p12 = PaginaDoce()
    p12.leer()
    kiosco.actualizar_diario(p12)

def subir_top_diez(string_fecha):

    kiosco = Kiosco()
    fecha = datetime.datetime.strptime(string_fecha, "%Y%m%d")

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nlp = NLP()
    for diario in config['diarios']:
        tag = diario['tag']
        twitter = diario['twitter']
    
        textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue

        texto = "Top 10 palabras más frecuentes en las noticias de " + twitter + " del " + fecha.strftime("%d.%m.%Y") + "\n"

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
        # api.update_with_media(filename=path_imagen, status=texto)

def subir_top_personas(string_fecha):
    kiosco = Kiosco()
    fecha = datetime.datetime.strptime(string_fecha, "%Y%m%d")

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nlp = NLP()
    for diario in config['diarios']:
        tag = diario['tag']
        twitter = diario['twitter']
    
        textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(diario=tag, fecha=fecha)]

        print("tag: " + tag +" textos: " + str(len(textos)))

        if len(textos) == 0:
            continue

        texto = "Top 10 personas más frecuentes en las noticias de " + twitter + " del " + fecha.strftime("%d.%m.%Y") + "\n"

        top_100 = nlp.top_personas(textos, n=100)

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

subir_top_personas(string_fecha="20190705")

def usage():
    print("dlm (dicen-los-medios) 2019 v1.1")
    print("--leer  actualiza las noticias de todos los diarios")
    print("--twittear=top  twittea el top 10 de todos los diarios")
    print("--fecha=AAAAMMDD  fecha de las noticias que usa para hacer el top 10")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["leer", "twittear=", "fecha="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    twittear=None
    string_fecha=""
    leer=False
    for o, a in opts:
        if o == "--leer":
            leer=True
        elif o == "--twittear":
            if a == "top":
                twittear=subir_top_diez
            else:
                print("análisis '" + a + "' no existe.")
                break
        elif o == "--fecha":
            string_fecha=a
        else:
            assert False, "opción desconocida"

    if leer:
        leer_diarios()

    if string_fecha:
        datetime.datetime.strptime(string_fecha, "%Y%m%d")
        twittear(string_fecha)

if __name__ == "__main__":
    main()