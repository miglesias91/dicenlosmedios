import time
import json
import datetime
from collections import defaultdict

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce
from ia import txt
from ia.txt import NLP
from bd.entidades import Fecha

def leer_diarios():

    string_fecha_de_hoy = datetime.date.today().strftime("%Y%m%d")

    hoy = Fecha(string_fecha_de_hoy)
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

def subir_a_dicenlosmedios():
    pass

# leer_diarios()

# freqs = txt.freq(textos)
# top_10 = freqs.most_common(10)
# print(top_10)

# freqs_bg = txt.freq_bigramas(textos)
# top_10_bg = freqs_bg.most_common(10)
# print(top_10_bg)

start = time.process_time()
textos = []
with open('textos.json', 'r', encoding='utf-8') as jsonfile:
    json_textos = json.load(jsonfile)
    textos = [jtexto for jtexto in json_textos['textos']]

nlp = NLP()
top_10 = nlp.top(textos)

print(time.process_time() - start)
print("", top_10)

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

