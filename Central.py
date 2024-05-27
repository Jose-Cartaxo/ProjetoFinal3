from Workers import *
from KNearest_Neighbors import * 
from typing import List, Dict, Any, Tuple
from Helper import *
from Optimization import *


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
    # lista de distancias vazia
    lista_distancias = []

    # percorrer o dicionário da classe
    for id, elemento in listaGruposCentral.lista_grupos_atividades.items():
        # se o id não estiver na lista
        if id not in central: 

            distancia = Distance_Calculator(elemento.centro[0], elemento.centro[1], x, y)
            lista_distancias.append([id, distancia])
    
    lista_distancias = sorted(lista_distancias, key=lambda x: x[1])

    primeiro_elemento = lista_distancias.pop(0)
    print('Central: ', primeiro_elemento[0])
    lista = listaGruposCentral.PesquisarPorId(primeiro_elemento[0])
    primeiro_elemento_atividades_estado_zero = [atividade for atividade in lista if atividade.state == 0]

    if len(primeiro_elemento_atividades_estado_zero) < k:
        primeiro_elemento_atividades_estado_zero.extend(CentralMaisProxima(listaGruposCentral, x, y, central.append(primeiro_elemento[0]), k - len(primeiro_elemento_atividades_estado_zero)))
    
    print(len(primeiro_elemento_atividades_estado_zero))
    return primeiro_elemento_atividades_estado_zero



def Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, k_nearest_neighbors, skills_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps):

    listaGruposCentral = Lista_Grupos_Central()
    
    for atividade in listaAtividades:
        listaGruposCentral.AdicionarGrupoId(atividade.idCentral, atividade)

    for blocoTrabalho in listaBlocoTrabalho:

        print('\n\n')
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        skills = trabalhador.skill
        central = trabalhador.idCentral
        print('Central do trabalhador: ', central)
        listaAtividadesGrupoCentral = listaGruposCentral.PesquisarPorId(central)

        atividades_estado_zero = [atividade for atividade in listaAtividadesGrupoCentral if atividade.state == 0]


        '''
            Se entrou aqui é porque na Central dele existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja não precisa de ir a outra central buscar mais atividades para complementar
        '''
        if len(atividades_estado_zero) > k_nearest_neighbors:
            listaAtividadesGrupoCentralPonderar = KNearest_Neighbors1(atividades_estado_zero, skills, blocoTrabalho, k_nearest_neighbors)


            '''
            Se entrou aqui é porque na Central dele não existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja precisa de ir a outra central buscar mais atividades para complementar
        '''
        else:
            lista_extend = CentralMaisProxima(listaGruposCentral, blocoTrabalho.x, blocoTrabalho.y, central, k_nearest_neighbors - len(atividades_estado_zero))
            atividades_estado_zero.extend(lista_extend)
            print('Valor final: ', len(atividades_estado_zero))
            listaAtividadesGrupoCentralPonderar = KNearest_Neighbors1(atividades_estado_zero, skills, blocoTrabalho, k_nearest_neighbors)

    nodes = Greedy(listaAtividadesGrupoCentralPonderar, blocoTrabalho, skills_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)




    # '''

    # colocar as atividades que foram atribuidas com o state == 1
    # '''
    # activitiesToState1(nodes, listaAtividades)

    # '''

    # fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock
    # '''
    # plot_activities_by_order(cluster, nodes, work_Block)

    # '''

    # colocar todas as atividades que não têm o state igual a 1 a 0
    # '''
    # for activity in listaAtividades:
    #     activity.resetStateToZeroIfNotOne()


    # '''

    # fazer um gráfico com a evolução da atribuição das atividades
    # '''
    # activityQuantity = len(nodes) - 2

    # meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    # if work_Block.start < meio_dia:
    #     list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
    # else:
    #     list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))





















    '''

    printar o tempo de execução do programa
    '''
    end_time = datetime.now() # type: ignore
    elapsed_time = end_time - start_time
    print("Tempo decorrido:", elapsed_time, "segundos")


    '''

    Análises estatísticas
    '''
    plot_activities_graph_by_state(listaAtividades)

    plot_heatmap_activities_by_state(listaAtividades)

    data = DataAnalyticsByHour(listaAtividades)
    sorted_stats_list = sorted(data)
    for dat in sorted_stats_list:
        dat.print()

    data = DataAnalyticsBySkill(listaAtividades)

    for dat in data:
        dat.print()



    print(type(data[0].tipo))
    plot_scatter_with_trendline(list_worker_activityQuantity)


    return