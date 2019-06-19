import string
import codecs
import multiprocessing
from collections import defaultdict

import nltk
from nltk.corpus import stopwords

import spacy

import gensim
from gensim.models.phrases import Phraser, Phrases
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

def freq_bigramas(textos):
    frecuencias = nltk.FreqDist()

    for texto in textos:
        
        palabras = __bolsa_de_palabras__(texto)

        # armo bigramas
        bigramas = nltk.bigrams(palabras)

        # calculo freqdist
        fdist = nltk.FreqDist(bigramas)

        for valor, freq in fdist.items():
            frecuencias[valor] = frecuencias.get(valor, 0) + freq
        
    return frecuencias

def word2vec_pro(textos):

    oraciones = __bolsa_de_oraciones_y_de_palabras_pro__(textos)

    frases = Phrases(oraciones, min_count=30, progress_per=10000)
    bigram = Phraser(frases)

    oraciones_con_bigramas = bigram[oraciones]

    word_freq = defaultdict(int)
    for sent in oraciones_con_bigramas:
        for i in sent:
            word_freq[i] += 1

    cores = multiprocessing.cpu_count() # Count the number of cores in a computer
    w2v_model = Word2Vec(min_count=20,
                     window=5,
                     size=300,
                     sample=6e-5, 
                     min_alpha=0.0007, 
                     negative=5,
                     workers=cores-1,
                     sg=1)
    
    w2v_model.build_vocab(oraciones_con_bigramas)

    w2v_model.train(oraciones_con_bigramas, total_examples=w2v_model.corpus_count, epochs=w2v_model.iter, report_delay=1)

    w2v_model.wv.init_sims(replace=True)

    return w2v_model, word_freq

def __bolsa_de_oraciones_y_de_palabras_pro__(textos):
    oraciones = []

    nlp = spacy.load('es_core_news_md', disable=['ner'])

    for texto in textos:

        doc = nlp(texto)
        
        for oracion in doc.sents:
            tokens = [token.lemma_ for token in oracion if not token.is_stop]

            palabras = __bolsa_de_palabras_pro__(tokens)

            oraciones.append(palabras)
        
    return oraciones

def __bolsa_de_palabras_pro__(palabras):
        # palabras = nltk.word_tokenize(texto)

        # saco numeros
        palabras = [palabra for palabra in palabras if not palabra.isnumeric()]

        # todo a minuscula
        palabras = [palabra.lower() for palabra in palabras]

        # hago stemming
        # stemmer = nltk.stem.snowball.SnowballStemmer('spanish')
        # palabras = [stemmer.stem(palabra) for palabra in palabras if palabra not in palabras]

        # saco signos de puntuacion
        signos = string.punctuation + "¡¿\n"
        palabras = [palabra.translate(str.maketrans('áéíóúý', 'aeiouy', signos)) for palabra in palabras]

        # saco stopwords
        locales_stopwords = codecs.open("stopwords.txt", 'r', encoding="utf-8").read().split("\r\n")
        # default_stopwords = set(nltk.corpus.stopwords.words('spanish'))
        # stopwords = default_stopwords | locales_stopwords
        palabras = [palabra for palabra in palabras if palabra not in locales_stopwords]

        # saco palabras de una sola letra y saco los espacios en blacno
        palabras = [palabra.strip() for palabra in palabras if len(palabra) > 1]

        # saco lugares vacios
        palabras = [palabra for palabra in palabras if palabra]

        return palabras

################

def word2vec(textos):

    oraciones = __bolsa_de_oraciones_y_de_palabras__(textos)

    return Word2Vec(oraciones, min_count=10, sg=1,)
    # cores = multiprocessing.cpu_count() # Count the number of cores in a computer
    # w2v_model = Word2Vec(min_count=20,
    #                  window=2,
    #                  size=300,
    #                  sample=6e-5, 
    #                  alpha=0.03, 
    #                  min_alpha=0.0007, 
    #                  negative=20,
    #                  workers=cores-1)
    
    # w2v_model.build_vocab(oraciones, progress_per=10000)

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
        # palabras = [stemmer.stem(palabra) for palabra in palabras if palabra not in palabras]

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

