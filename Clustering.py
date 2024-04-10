import math
from Workers import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from numpy import double
from Activity import *
def Travel_Time( travel_mult, x1, y1, x2, y2):
    return Distance_Calculator( x1, y1, x2, y2) * travel_mult # values_dict['TRAVEL_TIME']

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

def KNearest_Neighbors(list_activities, x, y, k):
    distances = []
    for activity in list_activities:
        distance = Distance_Calculator(activity.x, activity.y, x, y)
        distances.append((distance, activity))

    distances = sorted(distances, key=lambda x: x[0])
    list_temp = [tupla[1] for tupla in distances[:k]]
    return  list_temp
    

def DBSCANS(list_activities, x_Worker, y_Worker, cluster, distance_Min, distance_Max, iterations_Max):
    
    min_x_value = float('inf')
    max_x_value = float('-inf')
    min_y_value = float('inf')
    max_y_value = float('-inf')

    for i in range(iterations_Max): 
        print(i)
        radius = distance_Min
        previous_size = len(cluster)
        temp_cluster = []
        while previous_size == len(cluster) and radius <= distance_Max:
            for activity_clustered in cluster:
                for activity in list_activities:
                    if activity.state == 0:
                        distance = Distance_Calculator(activity.x, activity.y, activity_clustered.x, activity_clustered.y)
                        if distance < radius:
                            print('id: ', activity_clustered.idActivity, 'distance: ', distance, 'radius: ',radius)
                            temp_cluster.append(activity)
                            activity.state = 2

                            if activity.x  < min_x_value:
                                min_x_value = activity.x
                            if activity.x  > max_x_value:
                                max_x_value = activity.x

                            if activity.y  < min_y_value:
                                min_y_value = activity.y
                            if activity.y  > max_y_value:
                                max_y_value = activity.y


            if len( temp_cluster) == 0:
                print('Raio: ', radius, ' Não encontrou ninguém')
                radius += 1
            else:
                print('Raio: ', radius, ' Encontrou: ', len( temp_cluster))
                cluster.extend(temp_cluster)

    plot_activities_by_state(list_activities, x_Worker, y_Worker, min_x_value, max_x_value, min_y_value, max_y_value)
    return



def plot_heatmap_activities(list_activities):
    # Extrair coordenadas x, y e timestamps
    x_values = [task.x for task in list_activities]
    y_values = [task.y for task in list_activities]
    timestamps = [task.appointment.hour for task in list_activities]


    # Converter timestamps para valores numéricos para representar as cores
    # Por exemplo, você pode usar a hora do timestamp como o valor da cor
    color_values = [timestamp for timestamp in timestamps]

    # Criar heatmap
    plt.figure(figsize=(8, 6))
    heatmap = plt.scatter(x_values, y_values, c=color_values, cmap='viridis', s=100, alpha=0.7)
    plt.colorbar(heatmap, label='Hora da Marcação')
    plt.title('Heatmap das Atividades')
    plt.xlabel('X')
    plt.ylabel('Y')
    
    """

    for activity in all_Activities:
        plt.text(activity.x, activity.y, activity.skill, fontsize=8, ha='right', va='bottom')
    """

    # Mostrar o heatmap
    plt.show()





def plot_activities_by_state(list_activities, x_worker, y_worker, x_min, x_max, y_min, y_max):

    x_values = [activity.x for activity in list_activities]
    y_values = [activity.y for activity in list_activities]
    x_values.append(x_worker)
    y_values.append(y_worker)

    # Definir cores com base nos estados das tarefas
    cores = {0: 'red', 1: 'black', 2: 'green', 3: 'blue'}
    cores_pontos = [cores[activity.state] for activity in list_activities]
    cores_pontos.append(cores[3])
    
    plt.scatter(x_values, y_values, c=cores_pontos)
    plt.title('Gráfico de Coordenadas das Tarefas')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend(handles=[Line2D([], [], marker='o', color='red', label='Não contabilizadas', linestyle='None'),
                        Line2D([], [], marker='o', color='black', label='Ponto Partida', linestyle='None'),
                        Line2D([], [], marker='o', color='green', label='Contabilizadas', linestyle='None'),
                        Line2D([], [], marker='o', color='blue', label='Atribuidas', linestyle='None')],
                bbox_to_anchor=(1.05, 1), loc='upper left')
    

    # defenir o zoom inicial
    # plt.xlim(x_min - 0.3, x_max + 0.3)
    # plt.ylim(y_min - 0.3, y_max + 0.3)
    
    # Adicionar números para cada ponto
    for activity in list_activities:
        #print(i)
        if activity.appointment == -1:
            plt.text(activity.x, activity.y, str(-1), fontsize=8, ha='right', va='bottom')
        else:
            plt.text(activity.x, activity.y, activity.appointment.hour, fontsize=8, ha='right', va='bottom')
            """
            hour = str(activity.appointment.hour).zfill(2)  # zfill(2) adiciona um zero à esquerda, se necessário
            minutes = str(activity.appointment.minute).zfill(2)
            hour_minute = hour + ':' + minutes
            plt.text(activity.x, activity.y, hour_minute, fontsize=8, ha='right', va='bottom')
            """
    
    
    # plt.show(block=False)
    plt.show()
    return
