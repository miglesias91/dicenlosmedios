import os

from joblib import Parallel

import datetime
import string
import codecs
import multiprocessing
from collections import defaultdict

import nltk
from nltk.corpus import stopwords

import spacy
from spacy import tokens

import gensim
from gensim.models.phrases import Phraser, Phrases
from gensim.models import Word2Vec

from bd.entidades import Kiosco

def crear_nlp(path):
        path.mkdir(parents=True)
        nlp = spacy.load('es_core_news_md')
        nlp.to_disk(path)

class NLP:

    def __init__(self, path=None):
        self.nlp = spacy.load('es_core_news_md')
        self.verbos_lista = codecs.open("verbos.txt", 'r', encoding="utf-8").read().split("\r\n")
        self.sustantivos_lista = codecs.open("sustantivos.txt", 'r', encoding="utf-8").read().split("\r\n")
        self.ngramas = None
        self.separador = ' '

    def top(self, textos, n=10):

        top_t = self.top_terminos(textos, n)
        top_p = self.top_personas(textos, n)

        top_todo = top_t + top_p

        return sorted(top_todo, key=lambda tup: tup[1], reverse=True)[:n]


    def top_terminos(self, textos, n=10):
        oraciones = self.__bolsa_de_oraciones_y_palabras__(textos)

        frases = Phrases(oraciones, min_count=30, progress_per=10000)
        bigram = Phraser(frases)

        oraciones_con_bigramas = bigram[oraciones]

        word_freq = defaultdict(int)
        for sent in oraciones_con_bigramas:
            for i in sent:
                word_freq[i] += 1

        return [(k, word_freq[k]) for k in sorted(word_freq, key=word_freq.get, reverse=True)[:n]]

    def top_personas(self, textos, n=10):
        # recupero las noticias de los ultimos 3 dias para armar los bigramas
        hasta = datetime.datetime.now()
        desde = hasta - datetime.timedelta(days=3)

        # si todavia no se calcularon los ngramas, los calculo
        if self.ngramas == None:
            kiosco = Kiosco()
            set_entrenamiento = [noticia['titulo'] + " " + noticia['texto'] for noticia in kiosco.noticias(fecha={'desde':desde, 'hasta':hasta})]
            personas = self.__bolsa_de_personas__(set_entrenamiento)

            bifrases = Phrases(personas, min_count=3, threshold=2, progress_per=10000)
            bigramas = Phraser(bifrases)
            oraciones_con_bigramas = bigramas[personas]

            trifrases = Phrases(oraciones_con_bigramas, min_count=5, threshold=3, progress_per=10000)
            self.ngramas = Phraser(trifrases)

        personas = self.__bolsa_de_personas__(textos)
        personas_con_trigramas = self.ngramas[personas]

        personas_freq_tri = defaultdict(int)
        for sent in personas_con_trigramas:
            for i in sent:
                personas_freq_tri[i] += 1

        top_tri = {k: personas_freq_tri[k] for k in sorted(personas_freq_tri, key=personas_freq_tri.get, reverse=True)[:100]}

        nombres_a_borrar = []
        for nombre, freq in top_tri.items():
            for nombre_2, freq_2 in top_tri.items():
                if nombre != nombre_2 and nombre in nombre_2:
                    top_tri[nombre_2] += freq
                    if nombres_a_borrar.count(nombre) == 0:
                        nombres_a_borrar.append(nombre)

        for nombre in nombres_a_borrar:
            del top_tri[nombre]

        list_top_tri = [(k, top_tri[k]) for k in sorted(top_tri, key=top_tri.get, reverse=True) if k.count("_") > 0 ][:n]

        return [(concepto.replace('_', self.separador), numero) for concepto, numero in list_top_tri]

    def __bolsa_de_personas__(self, textos):
        personas = []

        signos = string.punctuation + "¡¿\n"
        for doc in self.nlp.pipe(textos, n_threads=16, batch_size=10000):
            for oracion in doc.sents:
                personas_ok = [entidad.text.translate(str.maketrans('','', signos)).split() for entidad in oracion.ents if entidad.label_ == "PER"]

                if len(personas_ok) == 0:
                    continue

                lista = []
                for persona in personas_ok:
                    lista += persona                     
                personas.append(lista)

        return personas

    def __bolsa_de_oraciones_y_palabras__(self, textos):
        oraciones = []

        for doc in self.nlp.pipe(textos, n_threads=16, batch_size=10000):
            for oracion in doc.sents:
                # saco las palabras que son entidades
                signos = string.punctuation + "¡¿\n"
                terminos_entidades = []
                [terminos_entidades.extend(ent.text.translate(str.maketrans('','', signos)).split()) for ent in oracion.ents]

                set_terminos_entidades = set(terminos_entidades)
                palabras_ok = [palabra.text for palabra in oracion if self.__es_relevante__(palabra=palabra) and palabra.text not in set_terminos_entidades]
                
                if len(palabras_ok) == 0:
                    continue
                
                oraciones.append(palabras_ok)

        return oraciones

    def __es_relevante__(self, palabra):
        if palabra.is_stop:
            return False

        if (palabra.pos_ != "NOUN") and (palabra.pos_ != "PROPN"):
            return False

        if palabra.lemma_.lower() in self.verbos_lista:
            return False

        if palabra.lemma_.lower() in self.sustantivos_lista:
            return False

        if palabra.is_digit:
            return False

        if len(palabra.text) <= 1:
            return False

        return True

    def __limpiar__(self, palabras):

        # saco numeros
        palabras = [palabra for palabra in palabras if not palabra.is_digit]

        # todo a minuscula
        palabras = [palabra.lower() for palabra in palabras]

        # saco signos de puntuacion
        signos = string.punctuation + "¡¿\n"
        palabras = [palabra.translate(str.maketrans('áéíóúý', 'aeiouy', signos)) for palabra in palabras]

        # saco stopwords
        locales_stopwords = codecs.open("stopwords.txt", 'r', encoding="utf-8").read().split("\r\n")

        palabras = [palabra for palabra in palabras if palabra not in locales_stopwords]

        # saco palabras de una sola letra y saco los espacios en blacno
        palabras = [palabra.strip() for palabra in palabras if len(palabra) > 1]

        # saco lugares vacios
        palabras = [palabra for palabra in palabras if palabra]

        return palabras