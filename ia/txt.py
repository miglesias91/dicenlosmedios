import os

from joblib import Parallel

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

def crear_nlp(path):
        path.mkdir(parents=True)
        nlp = spacy.load('es_core_news_md')
        nlp.to_disk(path)

class NLP:

    def __init__(self, path=None):
        self.nlp = spacy.load('es_core_news_md')
        self.verbos_lista = codecs.open("verbos.txt", 'r', encoding="utf-8").read().split("\r\n")
        self.sustantivos_lista = codecs.open("sustantivos.txt", 'r', encoding="utf-8").read().split("\r\n")

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
        oraciones = self.__bolsa_de_personas__(textos)

        bifrases = Phrases(oraciones, min_count=3, progress_per=10000)
        bigrams = Phraser(bifrases)
        oraciones_con_bigramas = bigrams[oraciones]

        trifrases = Phrases(oraciones_con_bigramas, min_count=3, progress_per=10000)
        trigrams = Phraser(trifrases)
        oraciones_con_trigramas = trigrams[oraciones_con_bigramas]

        personas_freq = defaultdict(int)
        for sent in oraciones_con_bigramas:
            for i in sent:
                personas_freq[i] += 1

        personas_freq_tri = defaultdict(int)
        for sent in oraciones_con_trigramas:
            for i in sent:
                personas_freq_tri[i] += 1

        personas_freq_limpio = defaultdict(int)
        signos = string.punctuation + "¡¿\n"
        for nombre, valor_apellido in personas_freq.items():
            personas_freq_limpio[nombre.translate(str.maketrans('','', signos))] = valor_apellido

        personas_freq = personas_freq_limpio

        a_borrar=[]
        for nombre, valor_apellido in personas_freq.items():
            campos_apellido = nombre.split()
            if len(campos_apellido) == 1:
                for apellido_y_nombre, valor_a_y_n in personas_freq.items():
                    if len(apellido_y_nombre.split()) > 1:
                        if apellido_y_nombre.split()[-1] == nombre:
                            personas_freq[apellido_y_nombre] += valor_apellido
                            if a_borrar.count(nombre) == 0:
                                a_borrar.append(nombre)
            if len(campos_apellido) == 2:
                for apellido_y_nombre, valor_a_y_n in personas_freq.items():
                    if len(apellido_y_nombre.split()) > 2:
                        if set(campos_apellido).issubset(apellido_y_nombre.split()):
                            personas_freq[apellido_y_nombre] += valor_apellido
                            if a_borrar.count(nombre) == 0:
                                a_borrar.append(nombre)

        for nombre in a_borrar:
            del personas_freq[nombre]

        return [(k, personas_freq[k]) for k in sorted(personas_freq, key=personas_freq.get, reverse=True)[:n]]

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

