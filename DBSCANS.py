import math
from re import L

from matplotlib.pylab import f
from Workers import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from Helper import *
# from numpy import block, double
from Activity import *
from Stats import *
from Ploting import *
from Optimization import *


def DBSCANS(list_activities: list [Activity], list_workers: list[Worker], work_Block: WorkBlock, cluster: list [Activity], distance_Min , distance_Max , iterations_Max):

    worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

    for i in range(iterations_Max):

        radius = distance_Min
        previous_size = len(cluster)
        temp_cluster = []

        while previous_size == len(cluster) and radius <= distance_Max:

            for activity_clustered in cluster:
                for activity in list_activities:
                    if activity.state == 0:
                        distance = Distance_Calculator(activity.latitude, activity.longitude, activity_clustered.latitude, activity_clustered.longitude)
                        if distance < radius:
                            if (activity.appointment < work_Block.fim and activity.appointment > work_Block.inicio) and (activity.competencia in worker.competencia):
                                temp_cluster.append(activity)
                                activity.state = 2

            if len( temp_cluster) == 0:
                radius += 1
            else:
                cluster.extend(temp_cluster)

    return cluster

def DBSCANS2(list_activities: list[Activity], list_workers: list[Worker], work_Block: WorkBlock, distance_Min, iterations_Max):
    """
    Esta função faz o clustering das atividades para o workblock.

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades a ponderar para o clustering.
    list_workers: (list of Workers)
        lista de todos os trabalhadores a ponderar para o clustering.
    work_Block: (Workblock)
        workblock a ponderar para o clustering.
    distance_Min: (Int)
        distancia minima utilizada para o raio de procura de atividades.
        workblock a ponderar para o clustering.
    distance_Max: (Int)
        distancia máxima utilizada para o raio de procura de atividades.
    iterations_Max: (Int)
        quantidade de iterações do DBSCANS.

    Returns
    -------
    list of Activity
        Retorna uma lista de atividades, que é o cluster final.
    """

    worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

    cluster = []
    
    radius = distance_Min
    temp_cluster = []


    for activity in list_activities:
        if activity.state == 0:
            distance = Distance_Calculator(activity.latitude, activity.longitude, work_Block.latitude, work_Block.longitude)
            # print('distancia = ', distance, ' Raio = ' , radius)
            if (distance < radius) and (activity.appointment < work_Block.fim) and (activity.appointment > work_Block.inicio or activity.appointment == time(0,0)) and (activity.competencia in worker.competencia):
                temp_cluster.append(activity)
                activity.state = 2


    cluster.extend(temp_cluster)
    print('Tamanho do cluster: ', len(cluster), end=', ')
    # print('temp_cluster Size = ', len(temp_cluster))


    for i in range(iterations_Max - 1):
        # print(i)
        temp_cluster.clear


        for activity_clustered in cluster:
            for activity in list_activities:
                if activity.state == 0:
                    distance = Distance_Calculator(activity.longitude, activity.latitude, activity_clustered.longitude, activity_clustered.latitude)
                    # print('distancia = ', distance, ' Raio = ' , radius)
                    if distance < radius and (activity.appointment < work_Block.fim) and (activity.appointment > work_Block.inicio or activity.appointment == time(0,0)) and (activity.competencia in worker.competencia):
                        temp_cluster.append(activity)
                        activity.state = 2

        # print('temp_cluster Size = ', len(temp_cluster))
        cluster.extend(temp_cluster)
        print(len(cluster), end=', ')

    # plot_activities_by_state(list_activities, work_Block)
    # print('Cluster Size = ', len(cluster) )
    return cluster



def DBSCANS3(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps):
    
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('listaAtividades: ', len(listaAtividades), ' listaTrabalhadores', len(listaTrabalhadores), ' listaBlocoTrabalho: ', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS: ', int(valores_dict['K_NEAREST_NEIGHBORS']))

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        competencias = trabalhador.competencia
        
        cluster = DBSCANS2(listaAtividades, listaTrabalhadores, blocoTrabalho, valores_dict['MAX_BDSCANS_DISTANCE'], int(valores_dict['DBSCANS_IT_NUM']))

        print('Size: ', len(cluster))
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
    return