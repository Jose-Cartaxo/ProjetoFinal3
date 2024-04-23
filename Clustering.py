import math

from matplotlib.pylab import f
from Workers import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from numpy import block, double
from Activity import *

# devolve a quantidade de Minutos necessários para relizar o trajeto
def Travel_Time( travel_mult, x1, y1, x2, y2):
    return Distance_Calculator( x1, y1, x2, y2) * travel_mult # values_dict['TRAVEL_TIME']

# devolve a distancia em KM entre 2 pontos
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

def KNearest_Neighbors(list_activities, workblock, k):
    distances = []
    for activity in list_activities:
        distance = Distance_Calculator(activity.x, activity.y, workblock.x, workblock.y)
        distances.append((distance, activity))

    distances = sorted(distances, key=lambda x: x[0])
    
    list_temp = []
    count = 0
    for tupla in distances:
        if (tupla[1].state == 0) and (tupla[1].appointment < workblock.finish) and (tupla[1].appointment > workblock.start) and (count < k):
            list_temp.append(tupla[1])
            tupla[1].state=2
            count += 1
    return  list_temp
    

def DBSCANS(list_activities, work_Block, cluster, distance_Min, distance_Max, iterations_Max):
    
    min_x_value = float('inf')
    max_x_value = float('-inf')
    min_y_value = float('inf')
    max_y_value = float('-inf')

    for i in range(iterations_Max): 
        # print(i)
        radius = distance_Min
        previous_size = len(cluster)
        temp_cluster = []
        while previous_size == len(cluster) and radius <= distance_Max:
            for activity_clustered in cluster:
                for activity in list_activities:
                    if activity.state == 0:
                        distance = Distance_Calculator(activity.x, activity.y, activity_clustered.x, activity_clustered.y)
                        if distance < radius and (activity.appointment < work_Block.finish and activity.appointment > work_Block.start):
                            # print('id: ', activity_clustered.idActivity, 'distance: ', distance, 'radius: ',radius)
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
                # print('Raio: ', radius, ' Não encontrou ninguém')
                radius += 1
            else:
                # print('Raio: ', radius, ' Encontrou: ', len( temp_cluster))
                cluster.extend(temp_cluster)

    # plot_activities_by_state(list_activities, work_Block)
    return


def plot_heatmap_activities_by_state(list_activities):
    # Extrair coordenadas x, y e timestamps
    x_values = [task.x for task in list_activities]
    y_values = [task.y for task in list_activities]
    timestamps = [task.state for task in list_activities]

    # Converter timestamps para valores numéricos para representar as cores
    # Por exemplo, você pode usar a hora do timestamp como o valor da cor
    color_values = [timestamp for timestamp in timestamps]

    # Criar heatmap
    plt.figure(figsize=(8, 6))
    heatmap = plt.scatter(x_values, y_values, c=color_values, cmap='viridis', s=100, alpha=0.7)
    plt.colorbar(heatmap, label='State')
    plt.title('Heatmap das Atividades por State')
    plt.xlabel('X')
    plt.ylabel('Y')

    # Mostrar o heatmap
    plt.savefig('PNG_Graphics/HeatMapState.png')
    plt.show()


def plot_heatmap_activities_by_hour(list_activities):
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
    plt.savefig('PNG_Graphics/HeatMap.png')
    plt.show(block = True)
    plt.close() 

def plot_activities_by_state(list_activities, work_Block):

    x_values = [activity.x for activity in list_activities]
    y_values = [activity.y for activity in list_activities]
    x_values.append(work_Block.x)
    y_values.append(work_Block.y)

    # Definir cores com base nos estados das tarefas
    cores = {0: 'red', 1: 'black', 2: 'green', 3: 'blue'}
    cores_pontos = [cores[activity.state] for activity in list_activities]
    cores_pontos.append(cores[3])
    
    plt.scatter(x_values, y_values, c=cores_pontos)
    plt.title('Cluster ' + str(work_Block.idWorker))
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend(handles=[Line2D([], [], marker='o', color='red', label='Não contabilizadas', linestyle='None'),
                        Line2D([], [], marker='o', color='black', label='Ponto Partida', linestyle='None'),
                        Line2D([], [], marker='o', color='green', label='Contabilizadas', linestyle='None'),
                        Line2D([], [], marker='o', color='blue', label='Atribuidas', linestyle='None')],
                bbox_to_anchor=(1.05, 1), loc='upper left')
    
    """

    for activity in list_activities:
        if activity.appointment == -1:
            plt.text(activity.x, activity.y, str(-1), fontsize=8, ha='right', va='bottom')
        else:
            plt.text(activity.x, activity.y, activity.idActivity, fontsize=8, ha='right', va='bottom')
    
    """

    
    plt.show(block=False)
    # plt.show(block=True)
    plt.close() 
    return

def plot_activities_by_order(list_activities, nodes, work_Block):
    
    activity_id_list = [node.id for node in nodes]

    x_values = []
    y_values = []
    points_colors = []

    x_values.append(work_Block.x)
    y_values.append(work_Block.y)
    points_colors.append(0)

    for num in activity_id_list:
        activity = Find_Activity_By_Id(list_activities, num)
        if activity:
            x_values.append(activity.x)
            y_values.append(activity.y)
            points_colors.append(3)

    x_values.append(work_Block.x)
    y_values.append(work_Block.y)
    points_colors.append(0)

    # Definir cores com base nos estados das tarefas
    colors = {0: 'black', 1: 'grey', 2: 'red', 3: 'green'}
    
    plt.figure(figsize=(12, 6))

    for i in range(len(x_values)-1):
        plt.arrow(x_values[i], y_values[i], x_values[i+1] - x_values[i], y_values[i+1] - y_values[i],
                color='blue', width=0.0005, head_width=0.007, length_includes_head=True)


    for activity in list_activities:
        if activity.idActivity not in activity_id_list:
            x_values.append(activity.x)
            y_values.append(activity.y)
            points_colors.append(activity.state)


    colors_order = [colors[color] for color in points_colors]
    

    plt.scatter(x_values, y_values, c=colors_order)
    plt.title(str(work_Block.idWorker) + ' Start:' + str(work_Block.start)+ ' End:' + str(work_Block.finish))
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')

    legend_elements = [
        Line2D([], [], marker='o', color='green', label='Atribuídas', linestyle='None'),
        Line2D([], [], marker='o', color='black', label='Ponto de Partida', linestyle='None'),
        Line2D([], [], marker='o', color='red', label='Não Atribuídas', linestyle='None')
    ]
    '''
    plt.legend(handles=[Line2D([], [], marker='o', color='green', label='Atribuidas', linestyle='None'),
                        Line2D([], [], marker='o', color='black', label='Ponto Partida', linestyle='None'),
                        Line2D([], [], marker='o', color='red', label='Não Atribuidas', linestyle='None')],
                        bbox_to_anchor=(1.05, 1), loc='upper left')


    for node in nodes:
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute)
            travel = '|Tr: ' + str(int(node.travel_Time))
            act = '|Ap: ' + str(activity.appointment.hour) + ':' + str(activity.appointment.minute)
            id = '|Id: ' + str(activity.idActivity)
            string =  id + act + travel + start
            plt.text(activity.x, activity.y, string, fontsize=9, ha='right', va='top')
    '''
    
    
    for i, node in enumerate(nodes):
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            id = str(i) + ' |Id: ' + str(activity.idActivity)
            ap = '|Ap: ' + str(activity.appointment.hour) + ':' + str(activity.appointment.minute).zfill(2)
            travel = '|Tr: ' + str(int(node.travel_Time))
            start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
            end = '|End: ' + str(node.end_Time.hour) + ':' + str(node.end_Time.minute).zfill(2)
            string =  id + ap + travel + start + end
            legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
        else:
            # worker = Find_Worker_By_Id(list_activities, node.id)
            if(i == 0):
                id = str(i) + ' |Id: ' + str(work_Block.idWorker)
                start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
                travel = '|Tr: ' + str(int(node.travel_Time))
                string =  id + start + travel
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
            else:
                id = str(i) + ' |Id: ' + str(work_Block.idWorker)
                travel = '|Tr: ' + str(int(node.travel_Time))
                start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
                string =  id + start + travel
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))

        

    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

    for activity in list_activities:
        if activity.idActivity not in activity_id_list:
            minute = str(activity.appointment.minute).zfill(2)
            hour = str(activity.appointment.hour)

            string = str(activity.idActivity) + ' | ' + hour + ':' + minute
            plt.text(activity.x, activity.y, string, fontsize=8, ha='right', va='bottom')

    plt.tight_layout()
    path = 'PNG_Graphics/' + str(work_Block.idWorker) + 'Block' + str(work_Block.idBlock) + '.png'
    
    plt.savefig(path)
    # plt.show(block=False)
    # plt.show(block=True)
    plt.close() 
    return

def plot_activities_graph_by_state(list_activities):
    list_states = [0,0]
    for activity in list_activities:
        list_states[activity.state] = list_states[activity.state] + 1 
    

    indices = range(len(list_states))

    # Criar o gráfico de barras
    plt.bar(indices, list_states)

    # Adicionar rótulos aos eixos
    plt.xlabel('State')
    plt.ylabel('Quantidade')

    # Adicionar título ao gráfico
    plt.title('Gráfico Quantidade por State')

    # Adicionar rótulos às barras
    for i, valor in enumerate(list_states):
        plt.text(i, valor, str(valor), ha='center', va='bottom')
    
    plt.show(block = True)
    plt.close() 