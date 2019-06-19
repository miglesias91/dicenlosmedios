from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce
from ia import txt

clarin = Clarin()
lanacion = LaNacion()
infobae = Infobae()
eldestape = ElDestape()
p12 = PaginaDoce()

# clarin.leer()
# lanacion.leer()
infobae.leer()
# p12.leer()
# eldestape.leer()
textos = []
textos += [noticia.titulo + " " + noticia.titulo + " " + noticia.texto for noticia in infobae.categorias['politica']]
textos += [noticia.titulo + " " + noticia.titulo + " " + noticia.texto for noticia in infobae.categorias['economia']]
textos += [noticia.titulo + " " + noticia.titulo + " " + noticia.texto for noticia in infobae.categorias['internacional']]
textos += [noticia.titulo + " " + noticia.titulo + " " + noticia.texto for noticia in infobae.categorias['sociedad']]



# freqs = txt.freq(textos)
# top_10 = freqs.most_common(10)
# print(top_10)

# freqs_bg = txt.freq_bigramas(textos)
# top_10_bg = freqs_bg.most_common(10)
# print(top_10_bg)

word_freq = {}
modelo, word_freq = txt.word2vec_pro(textos)
top_10 = sorted(word_freq, key=word_freq.get, reverse=True)[:10]

# print(modelo.wv.most_similar(top_10[0][0], topn=5))
print(top_10)
print(modelo.wv.most_similar(['kirchnerismo'], topn=5))
print(modelo.wv.most_similar(['cristina_kirchner'], topn=5))
print(modelo.wv.most_similar(['mauricio_macri'], topn=5))
print(modelo.wv.most_similar(['policia'], topn=5))
print(modelo.wv.most_similar(['dolar'], topn=5))
print(modelo.wv.similar_by_word(top_10[0], topn=5))

hola = 0

