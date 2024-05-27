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
    quantidadeGrupos = 0

    def __init__(self):
        self.lista_grupos_atividades = {}

        Lista_Grupos_Central.quantidadeGrupos += 1

    def PesquisarPorId(self, id)-> List[Activity]:
        return self.lista_grupos_atividades.get(id, None).lista_atividades
    
    def AdicionarGrupoId(self, id, atividade):
        if id in self.lista_grupos_atividades:
            self.lista_grupos_atividades[id].AdicionarAtividade(atividade)
        else:
            self.lista_grupos_atividades[id] = Elemento_Lista_Grupos_Central(atividade)
        
    def CalcularTodosCentros(self):
        for elemento in self.lista_grupos_atividades.values():
            elemento.CalcularCentro()



def CentralMaisProxima(listaGruposCentral, x, y, central, k) -> List[Activity]:
    if len(central) < 5:
        # lista de distancias vazia
        lista_distancias = []
        # print('"CentralMaisProxima - K" = ', k, ' Size Central', len(central))

        # percorrer o dicionário da classe
        for id, elemento in listaGruposCentral.lista_grupos_atividades.items():
            # se o id não estiver na lista
            if id not in central: 

                distancia = Distance_Calculator(elemento.centro[0], elemento.centro[1], x, y)
                lista_distancias.append([id, distancia])
        
        lista_distancias = sorted(lista_distancias, key=lambda x: x[1])

        primeiro_elemento = lista_distancias.pop(0)
        # print('Central: ', primeiro_elemento[0])
        lista = listaGruposCentral.PesquisarPorId(primeiro_elemento[0])
        primeiro_elemento_atividades_estado_zero = [atividade for atividade in lista if atividade.state == 0]

        if len(primeiro_elemento_atividades_estado_zero) < k:
            primeiro_elemento_atividades_estado_zero.extend(CentralMaisProxima(listaGruposCentral, x, y, central.append(primeiro_elemento[0]), k - len(primeiro_elemento_atividades_estado_zero)))
        
        # print(len(primeiro_elemento_atividades_estado_zero))
        return primeiro_elemento_atividades_estado_zero
    return []


def Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, k_nearest_neighbors, skills_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps):

    listaGruposCentral = Lista_Grupos_Central()
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []
    
    for atividade in listaAtividades:
        listaGruposCentral.AdicionarGrupoId(atividade.idCentral, atividade)

    for blocoTrabalho in listaBlocoTrabalho:

        # print('\n\n')
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        skills = trabalhador.skill
        central = trabalhador.idCentral
        # print('Central do trabalhador: ', central)
        listaAtividadesGrupoCentral = listaGruposCentral.PesquisarPorId(central)

        atividades_estado_zero = [atividade for atividade in listaAtividadesGrupoCentral if atividade.state == 0 and atividade.skill in skills]


        '''
            Se entrou aqui é porque na Central dele existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja não precisa de ir a outra central buscar mais atividades para complementar
        '''
        if len(atividades_estado_zero) > k_nearest_neighbors:
            print(trabalhador.idWorker, 'A zona dele chega para ele!')
            cluster = KNearest_Neighbors1(atividades_estado_zero, skills, blocoTrabalho, k_nearest_neighbors)
            print('Ficou com ', len(cluster), ' atividades para fazer\n\n' )


            '''
            Se entrou aqui é porque na Central dele não existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja precisa de ir a outra central buscar mais atividades para complementar
        '''
        else:
            k = k_nearest_neighbors - len(atividades_estado_zero)
            print(trabalhador.idWorker, 'A zona dele NÃO dá ele!')

            # print('k_nearest_neighbors = ', k_nearest_neighbors,' len = ',len(atividades_estado_zero),' "K" = ', k)
            lista_extend = CentralMaisProxima(listaGruposCentral, blocoTrabalho.x, blocoTrabalho.y, [central], k)
            atividades_estado_zero.extend(lista_extend)
            # print('Valor final: ', len(atividades_estado_zero))
            cluster = KNearest_Neighbors1(atividades_estado_zero, skills, blocoTrabalho, k_nearest_neighbors)
            print('Ficou com ', len(cluster), ' atividades para fazer\n\n' )

        nodes = Greedy(cluster, blocoTrabalho, skills_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)


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

        if blocoTrabalho.start < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)
    return