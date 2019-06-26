# import spacy
# from spacy.lang.es.examples import sentences 

# nlp = spacy.load('es_core_news_md')
# doc = nlp(sentences[0])
# print(doc.text)
# for token in doc:
#     print(token.text, token.pos_, token.dep_)



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

    string_fecha_de_hoy = datetime.date.today().strftime("%Y%m%d")

    hoy = Kiosco(string_fecha_de_hoy)
    hoy.recuperar()

    # infobae.com
    infobae = Infobae()
    infobae.leer()
    hoy.agregar(infobae)

    # clarin.com
    clarin = Clarin()
    clarin.leer()
    hoy.agregar(clarin)

    # lanacion.com
    lanacion = LaNacion()
    lanacion.leer()
    hoy.agregar(lanacion)

    # eldestapeweb.com
    eldestape = ElDestape()
    eldestape.leer()
    hoy.agregar(eldestape)

    # pagina12.com
    p12 = PaginaDoce()
    p12.leer()
    hoy.agregar(p12)

    hoy.guardar()

def subir_a_dicenlosmedios(string_fecha):

    kiosco = Kiosco(string_fecha)
    kiosco.recuperar()

    with open('medios/diarios/config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    path = pathlib.Path().cwd() / "modelos/es"
    nlp = NLP(path)
    for diario in config['diarios']:
        tag = diario['tag']
        twitter = diario['twitter']
    
        textos = [noticia['titulo'] + " " + noticia['titulo'] + " " + noticia['titulo'] for noticia in kiosco.noticias(diario=tag)]

        if len(textos) == 0:
            continue

        fecha = datetime.datetime.strptime(string_fecha, "%Y%m%d")
        texto = "Top 10 palabras más frecuentes en las noticias de " + twitter + " del " + fecha.strftime("%d.%m.%Y") + "\n"

        top_100 = nlp.top(textos, 100)

        i = 0
        for nombre, m in top_100:
            linea = ""
            i += 1
            if i >= 10:
                linea = str(i) + ". #" + nombre + "\n"
                texto += linea
                break
            else:
                linea = str(i) + ".  #" + nombre + "\n"

            if len(texto) + len(linea) < 220:
                texto += linea
            else:
                break

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
        path_imagen = "infobae" + ".png"
        wordcloud.to_file(path_imagen)
        api.update_with_media(filename=path_imagen, status=texto)

# leer_diarios()

# subir_a_dicenlosmedios(string_fecha="20190621")

start = time.process_time()
textos = []
with open('textos.json', 'r', encoding='utf-8') as jsonfile:
    json_textos = json.load(jsonfile)
    textos = [jtexto for jtexto in json_textos['textos']]


path = pathlib.Path().cwd() / "modelos/es"
# txt.crear_nlp(path=path)

nlp = NLP(path)
top_100 = nlp.top(textos, n=100)

print(time.process_time() - start)
print("", top_100)

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
path_imagen = "infobae" + ".png"
wordcloud.to_file(path_imagen)

start = time.process_time()
word_freq = defaultdict(int)
word_freq = txt.word2vec_pro(textos)
top_10 = [(k, word_freq[k]) for k in sorted(word_freq, key=word_freq.get, reverse=True)[:10]]

print(time.process_time() - start)
print(top_10)

# # print(modelo.wv.most_similar(top_10[0][0], topn=5))
# print(top_10)
# print(modelo.wv.most_similar(['kirchnerismo'], topn=5))
# print(modelo.wv.most_similar(['cristina_kirchner'], topn=5))
# print(modelo.wv.most_similar(['mauricio_macri'], topn=5))
# print(modelo.wv.most_similar(['policia'], topn=5))
# print(modelo.wv.most_similar(['dolar'], topn=5))
# print(modelo.wv.similar_by_word(top_10[0], topn=5))

# hola = 0

