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


def DBSCANS(list_activities, list_workers, work_Block, cluster, distance_Min, distance_Max, iterations_Max):

    worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

    for i in range(iterations_Max):

        radius = distance_Min
        previous_size = len(cluster)
        temp_cluster = []

        while previous_size == len(cluster) and radius <= distance_Max:

            for activity_clustered in cluster:
                for activity in list_activities:
                    if activity.state == 0:
                        distance = Distance_Calculator(activity.x, activity.y, activity_clustered.x, activity_clustered.y)
                        if distance < radius and (activity.appointment < work_Block.finish and activity.appointment > work_Block.start) and (activity.skill in worker.skill): # type: ignore
                            # print('id: ', activity_clustered.idActivity, 'distance: ', distance, 'radius: ',radius)
                            temp_cluster.append(activity)
                            activity.state = 2

            if len( temp_cluster) == 0:
                # print('Raio: ', radius, ' Não encontrou ninguém')
                radius += 1
            else:
                # print('Raio: ', radius, ' Encontrou: ', len( temp_cluster))
                cluster.extend(temp_cluster)

    # plot_activities_by_state(list_activities, work_Block)
    return cluster

def DBSCANS2(list_activities, list_workers, work_Block, distance_Min, iterations_Max):
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
            distance = Distance_Calculator(activity.x, activity.y, work_Block.x, work_Block.y)
            # print('distancia = ', distance, ' Raio = ' , radius)
            if (distance < radius) and (activity.appointment < work_Block.finish) and (activity.appointment > work_Block.start) and (activity.skill in worker.skill): # type: ignore
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
                    distance = Distance_Calculator(activity.x, activity.y, activity_clustered.x, activity_clustered.y)
                    # print('distancia = ', distance, ' Raio = ' , radius)
                    if distance < radius and (activity.appointment < work_Block.finish and activity.appointment > work_Block.start) and (activity.skill in worker.skill): # type: ignore
                        temp_cluster.append(activity)
                        activity.state = 2

        
        # print('temp_cluster Size = ', len(temp_cluster))
        cluster.extend(temp_cluster)
        print(len(cluster), end=', ')



    # plot_activities_by_state(list_activities, work_Block)
    # print('Cluster Size = ', len(cluster) )
    return cluster