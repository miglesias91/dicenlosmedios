import string
import codecs

import nltk
from nltk.corpus import stopwords

import gensim
from gensim.models import Word2Vec

def freq(textos):
    frecuencias = nltk.FreqDist()

    for texto in textos:
        
        palabras = __bolsa_de_palabras__(texto)

        # calculo freqdist
        fdist = nltk.FreqDist(palabras)

        for valor, freq in fdist.items():
            frecuencias[valor] = frecuencias.get(valor, 0) + freq
        
    return frecuencias


def word2vec(textos):

    oraciones = __bolsa_de_oraciones_y_de_palabras__(textos)

    return Word2Vec(oraciones, min_count=10, sg=1)



def __bolsa_de_oraciones_y_de_palabras__(textos):
    oraciones = []

    for texto in textos:

        for oracion in nltk.sent_tokenize(texto):

            palabras = __bolsa_de_palabras__(oracion)

            oraciones.append(palabras)
        
    return oraciones

def __bolsa_de_palabras__(texto):
        palabras = nltk.word_tokenize(texto)

        # saco numeros
        palabras = [palabra for palabra in palabras if not palabra.isnumeric()]

        # todo a minuscula
        palabras = [palabra.lower() for palabra in palabras]

        # hago stemming
        # stemmer = nltk.stem.snowball.SnowballStemmer('spanish')
        # palabras = [stemmer.stem(palabra) for palabra in palabras]

        # saco stopwords
        locales_stopwords = set(codecs.open("stopwords.txt", 'r').read().split("\n"))
        default_stopwords = set(nltk.corpus.stopwords.words('spanish'))
        stopwords = default_stopwords | locales_stopwords
        palabras = [palabra for palabra in palabras if palabra not in stopwords]

        # saco signos de puntuacion
        signos = string.punctuation + "¡¿"
        palabras = [palabra.translate(str.maketrans('áéíóúý', 'aeiouy', signos)) for palabra in palabras]

        # saco palabras de una sola letra
        palabras = [palabra for palabra in palabras if len(palabra) > 1]

        # saco lugares vacios
        palabras = [palabra for palabra in palabras if palabra]

        return palabras

