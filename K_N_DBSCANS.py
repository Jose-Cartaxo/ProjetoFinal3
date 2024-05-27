from KNearest_Neighbors import *
from DBSCANS import *
from Optimization import *
from Ploting import *
from Stats import *

def K_N_DBSCANS(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, skills_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps):
    
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('listaAtividades: ', len(listaAtividades), ' listaTrabalhadores', len(listaTrabalhadores), ' listaBlocoTrabalho: ', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS: ', int(valores_dict['K_NEAREST_NEIGHBORS']))

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        skills = trabalhador.skill
        
        cluster = KNearest_Neighbors1(listaAtividades, skills, blocoTrabalho, 4)
        cluster = DBSCANS(listaAtividades, listaTrabalhadores, blocoTrabalho, cluster, valores_dict['MIN_BDSCANS_DISTANCE'], valores_dict['MAX_BDSCANS_DISTANCE'], int(valores_dict['DBSCANS_IT_NUM']))

        print('Size: ', len(cluster))
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
        activityQuantity = len(nodes) - 1
        # activityQuantity = len(nodes) - 2

        if blocoTrabalho.start < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)
    return