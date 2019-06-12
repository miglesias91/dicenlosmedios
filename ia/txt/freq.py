import string
import codecs

import nltk

from nltk.corpus import stopwords

def freq(textos):
    frecuencias = nltk.FreqDist()

    for texto in textos:
        palabras = nltk.word_tokenize(texto)

        # saco numeros
        palabras = [palabra for palabra in palabras if not palabra.isnumeric()]

        # todo a minuscula
        palabras = [palabra.lower() for palabra in palabras]

        # hago stemming
        # stemmer = nltk.stem.snowball.SnowballStemmer('spanish')
        # palabras = [stemmer.stem(palabra) for palabra in palabras]

        # saco stopwords
        stopwords = set(nltk.corpus.stopwords.words('spanish'))
        palabras = [palabra for palabra in palabras if palabra not in stopwords]

        # saco signos de puntuacion
        signos = string.punctuation + "¡¿"
        palabras = [palabra.translate(str.maketrans('', '', signos)) for palabra in palabras]

        # saco palabras de una sola letra
        palabras = [palabra for palabra in palabras if len(palabra) > 1]

        # saco lugares vacios
        palabras = [palabra for palabra in palabras if palabra]

        # calculo freqdist
        fdist = nltk.FreqDist(palabras)

        for valor, freq in fdist.items():
            frecuencias[valor] = frecuencias.get(valor, 0) + freq
        
    return frecuencias
