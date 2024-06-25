from KNearest_Neighbors import *
from DBSCAN import *
from Optimization import *
from Ploting import *
from Stats import *

def Opcao_K_N_DBSCAN(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], competencias_dict, valores_dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    
    meio_dia = datetime.datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('listaAtividades: ', len(listaAtividades), ' listaTrabalhadores', len(listaTrabalhadores), ' listaBlocoTrabalho: ', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS: ', int(valores_dict['K_NEAREST_NEIGHBORS']), 'MIN_DBSCAN_DISTANCE: ', valores_dict['MIN_DBSCAN_DISTANCE'], 'MAX_DBSCAN_DISTANCE: ', valores_dict['MAX_DBSCAN_DISTANCE'], 'DBSCANS_IT_NUM: ', int(valores_dict['DBSCAN_IT_NUM']))

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        competencias = trabalhador.competencia
        
        cluster = KNearest_Neighbors_Normal(listaAtividades, competencias, blocoTrabalho, 4)
        cluster = DBSCAN1(listaAtividades, listaTrabalhadores, blocoTrabalho, cluster, valores_dict['MIN_DBSCAN_DISTANCE'], valores_dict['MAX_DBSCAN_DISTANCE'], int(valores_dict['DBSCAN_IT_NUM']))

        nodes = Greedy(cluster, blocoTrabalho, competencias_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

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
        activityQuantity = len(nodes) - 1
        # activityQuantity = len(nodes) - 2

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