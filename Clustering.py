import math
from Workers import *
import matplotlib.pyplot as plt

from numpy import double
from activity import *


def Distance_Calculator( x1, y1, x2, y2):
    R = 6373.0

    lat1 = math.radians(x1)
    lon1 = math.radians(y1)
    lat2 = math.radians(x2)
    lon2 = math.radians(y2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def KNearest_Neighbors(all_Activities, x, y, k):
    distances = []
    for activity in all_Activities:
        distance = Distance_Calculator(activity.x, activity.y, x, y)
        distances.append((distance, activity))

    distances = sorted(distances, key=lambda x: x[0])
    list_temp = [tupla[1] for tupla in distances[:k]]
    return  list_temp
    

def DBSCANS(all_activities, cluster, distance_Min, distance_Max, iterations_Max):
    
    for i in range(iterations_Max): 
        print(i)
        radius = distance_Min
        previous_size = len(cluster)
        while previous_size == len(cluster) and radius <= distance_Max:
            for activity_clustered in cluster:
                for activity in all_activities:
                    if activity.state == 0:
                        distance = Distance_Calculator(activity.x, activity.y, activity_clustered.x, activity_clustered.y)
                        if distance < radius:
                            print('id: ' , activity_clustered.idActivity ,'distance: ', distance, 'radius: ',radius)
                            cluster.append(activity)
                            activity.state = 2

            if previous_size == len(cluster):
                print('Não foi encontrado ninguém, radius = ', radius, 'Cluster size = ', len(cluster))
                radius += 1
    return

def plot_activities_by_state(all_Activities):
    # Extrair as coordenadas x e y em listas separadas
    x = [activity.x for activity in all_Activities]
    y = [activity.y for activity in all_Activities]
    
    # Definir cores com base nos estados das tarefas
    cores = {'concluido': 'green', 'em_progresso': 'blue', 'pendente': 'red'}
    cores_pontos = [activity.state for activity in all_Activities]
    
    # Criar o gráfico de dispersão com cores diferentes para os pontos
    plt.scatter(x, y, c=cores_pontos)
    plt.title('Gráfico de Coordenadas das Tarefas')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend(handles=[plt.Line2D([], [], marker='o', color='green', label='Concluído', linestyle='None'),
                        plt.Line2D([], [], marker='o', color='blue', label='Em progresso', linestyle='None'),
                        plt.Line2D([], [], marker='o', color='red', label='Pendente', linestyle='None')])
    
    # Mostrar o gráfico
    plt.show()
    return