import unittest

import newspaper as np

from medios.diarios.diarios import Clarin, ElDestape, Infobae, LaNacion, PaginaDoce

class TestMedios(unittest.TestCase):

    def test_limpiar_texto_clarin(self):
        articulo = np.Article(url="http://www.clarin.com/politica/roberto-lavagna-promete-empezar-acompanar-juan-manuel-urtubey-recorridas-campana_0_XFVKj9fDb.html", language='es')
        articulo.download()
        articulo.parse()

        diario = Clarin()
        t = diario.limpiar_texto(articulo.text)
        return 1
    
    def test_limpiar_texto_lanacion(self):
        articulo = np.Article(url="https://www.lanacion.com.ar/politica/un-legislador-tucumano-quiere-declarar-persona-no-nid2264493", language='es')
        articulo.download()
        articulo.parse()

        diario = LaNacion()
        t = diario.limpiar_texto(articulo.text)
        return 1
