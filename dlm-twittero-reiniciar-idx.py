from bd.entidades import Kiosco

# solo reinicio el idx = 1
k = Kiosco()
k.bd.temp.replace_one({'clave':'indice-twittero'}, {'clave':'indice-twittero', 'idx':1}, upsert=True)