from Workers import *
from KNearest_Neighbors import * 
from typing import List, Dict, Any, Tuple

class Elemento_Lista_Grupos_Central:
    
    def __init__(self, atividade):
        self.centro = [0,0]
        self.lista_atividades = [atividade]

    def AdicionarAtividade(self, atividade):
        self.lista_atividades.append(atividade)

    def CalcularCentro(self):
        x_total = 0
        y_total = 0
        for atividade in self.lista_atividades:
            x_total += atividade.x
            y_total += atividade.y

        x_medio = x_total / len(self.lista_atividades)
        y_medio = y_total / len(self.lista_atividades)
        self.centro = [x_medio, y_medio]




class Lista_Grupos_Central:
    quantidadeGrupos = 0

    def __init__(self):
        self.lista_grupos_atividades = {}

        Lista_Grupos_Central.quantidadeGrupos += 1

    def PesquisarPorId(self, id):
        return self.lista_grupos_atividades.get(id, None)
    
    def AdicionarGrupoId(self, id, atividade):
        if id in self.lista_grupos_atividades:
            self.lista_grupos_atividades[id].AdicionarElemento(atividade)
        else:
            self.lista_grupos_atividades[id] = Elemento_Lista_Grupos_Central(atividade)




def Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho):

    listaGruposCentral = Lista_Grupos_Central()
    
    for atividade in listaAtividades:
        listaGruposCentral.AdicionarGrupoId(atividade.id, atividade)

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idworker)
        skills = trabalhador.skill
        listaAtividadesGrupoCentral = listaGruposCentral.PesquisarPorId(trabalhador.idCentral)

        listaAtividadesGrupoCentralPonderar = KNearest_Neighbors1(listaAtividadesGrupoCentral, skills, blocoTrabalho, 10)





