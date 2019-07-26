import yaml
import datetime
from itertools import permutations, repeat

import dlm
from bd.entidades import Kiosco

with open('medios/diarios/config.yaml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

tag_medios = [diario['tag'] for diario in config['diarios'] if diario['tag'] != 'casarosada']
categorias = ['politica', 'economia', 'sociedad', 'internacional', 'deportes', 'espectaculos', 'cultura']

tuplas_tag_cat = []
for tag in tag_medios:
    for cat in categorias:
        tuplas_tag_cat.append((tag, cat))

k = Kiosco()

# recupero el indice
indice_twittero = k.bd.temp.find_one({'clave':'indice-twittero'})

idx = 0
if indice_twittero or idx > len(tuplas_tag_cat):
    idx = indice_twittero['idx']
    # actualizo el indice de la bd: lo incremento en 1
    k.bd.temp.update_one({'clave':'indice-twittero'}, {'$inc':{'idx':1}})
else:
    # si no existe el indice o ya supero el numero total de tuplas, entonces lo reseteo a 0
    k.bd.temp.replace_one({'clave':'indice-twittero'}, {'clave':'indice-twittero', 'idx':1}, upsert=True)

tupla = tuplas_tag_cat[idx]
fecha = datetime.datetime.now().date() - datetime.timedelta(days=1)

parametros = {'medios':[tupla[0]], 'top_max':100, 'fecha':fecha, 'twittear':True, 'solo_titulos':False, 'categorias':[tupla[1]]}

dlm.top_todo(parametros)