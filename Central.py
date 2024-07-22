from numpy import double
from Workers import *
from KNearest_Neighbors import * 
from typing import List, Dict, Any, Tuple
from Helper import *
from Optimization import *
from Ploting import *
from Stats import *

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
    """Dicionário com o id da central e a lista de atividades que pertencem a essa central.

    Returns:
        _type_: _description_
    """
    quantidadeGrupos = 0

    def __init__(self):
        self.lista_grupos_atividades: dict = {}

    def PesquisarPorId(self, idCentral)-> list[Activity]:
        return self.lista_grupos_atividades.get(idCentral, None).lista_atividades
    
    def AdicionarGrupoId(self, idCentral, atividade):
        if idCentral in self.lista_grupos_atividades:
            self.lista_grupos_atividades[idCentral].AdicionarAtividade(atividade)
        else:
            self.lista_grupos_atividades[idCentral] = Elemento_Lista_Grupos_Central(atividade)
            Lista_Grupos_Central.quantidadeGrupos += 1
        
    def CalcularTodosCentros(self):
        for elemento in self.lista_grupos_atividades.values():
            elemento.CalcularCentro()



def CentralMaisProxima(listaGruposCentral: Lista_Grupos_Central, lat: float, lon: float, central, k: int) -> list[Activity]:

    if len(central) < 5:
        # lista de distancias vazia
        lista_distancias = []
        # print('"CentralMaisProxima - K" = ', k, ' Size Central', len(central))

        # percorrer o dicionário da classe
        for id, elemento in listaGruposCentral.lista_grupos_atividades.items():
            # se o id não estiver na lista
            if id not in central: 

                distancia = Distance_Calculator(elemento.centro[0], elemento.centro[1], lat, lon)
                lista_distancias.append([id, distancia])
        
        lista_distancias = sorted(lista_distancias, key=lambda x: x[1])

        primeiro_elemento = lista_distancias.pop(0)
        # print('Central: ', primeiro_elemento[0])
        lista = listaGruposCentral.PesquisarPorId(primeiro_elemento[0])
        primeiro_elemento_atividades_estado_zero = [atividade for atividade in lista if atividade.state == 0]

        if len(primeiro_elemento_atividades_estado_zero) < k:
            primeiro_elemento_atividades_estado_zero.extend(CentralMaisProxima(listaGruposCentral, lat, lon, central.append(primeiro_elemento[0]), k - len(primeiro_elemento_atividades_estado_zero)))
        
        # print(len(primeiro_elemento_atividades_estado_zero))
        return primeiro_elemento_atividades_estado_zero
    return []


def Opcao_Agrupamento_Por_Central(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], k_nearest_neighbors: int, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps):


    # Aqui guarda a hora "11:00" para depois comparar os blocos de trabalho da parte da manha e da parte da tarde
    meio_dia: time = datetime.strptime('11:00:00', '%H:%M:%S').time()

    # lista com a quantidade de atividades realizadas pelos trabalhadores, por ordem
    list_worker_activityQuantity: list[WorkBlockStats] = []

    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))


    # Aqui vão ficar as atividades separadas por Central
    listaGruposCentral = preencherListaCentral(listaAtividades)

    '''
        Fazer a atribuição para casa um dos blocos de trabalho
    '''

    for blocoTrabalho in listaBlocoTrabalho:

        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        competencias = trabalhador.competencia
        central = trabalhador.idCentral

        listaAtividadesGrupoCentral = listaGruposCentral.PesquisarPorId(central)

        atividades_estado_zero = [atividade for atividade in listaAtividadesGrupoCentral if atividade.state == 0 and atividade.competencia in competencias]


        if len(atividades_estado_zero) > k_nearest_neighbors:
            '''
                Se entrou aqui é porque na Central dele existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja não precisa de ir a outra central buscar mais atividades para complementar
            '''

            cluster = KNearest_Neighbors_Normal(atividades_estado_zero, competencias, blocoTrabalho, k_nearest_neighbors)



        else:
            '''
                Se entrou aqui é porque na Central dele não existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja precisa de ir a outra central buscar mais atividades para complementar
            '''
            
            k = k_nearest_neighbors - len(atividades_estado_zero)

            lista_extend = CentralMaisProxima(listaGruposCentral, blocoTrabalho.latitude, blocoTrabalho.longitude, [central], k)
            atividades_estado_zero.extend(lista_extend)
            
            cluster = KNearest_Neighbors_Normal(atividades_estado_zero, competencias, blocoTrabalho, k_nearest_neighbors)

        nodes = Greedy(cluster, blocoTrabalho, dicionario_distancias, competencias_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)


        '''

        colocar as atividades que foram atribuidas com o state == 1
        '''
        activitiesToState1(nodes, listaAtividades)

        '''

        fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock


        '''
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        '''

        colocar todas as atividades que não têm o state igual a 1 a 0
        '''
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()


        '''

        fazer um gráfico com a evolução da atribuição das atividades
        '''
        activityQuantity = len(nodes) - 2

        if blocoTrabalho.inicio < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)
    
    print('\nManha \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'manha':
            print(stat.quantidade, end=", ")
    print('\n\nTarde \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'tarde':
            print(stat.quantidade, end=", ")
    print('\n')

    return

def preencherListaCentral(listaAtividades):
    '''
    Criar um grupo para cada atividade
    '''
    listaGruposCentral = Lista_Grupos_Central()
    for atividade in listaAtividades:
        listaGruposCentral.AdicionarGrupoId(atividade.idCentral, atividade)
    return listaGruposCentral