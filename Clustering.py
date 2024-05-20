import math
from re import L

from matplotlib.pylab import f
from Workers import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
# from numpy import block, double
from Activity import *

# def Gra

'''
def Travel_Time( x1, y1, x2, y2, gmaps):
    origem = (x1, y1)  # San Francisco, CA
    destino = (x2, y2)  # Los Angeles, CA
    result = gmaps.distance_matrix(origem, destino, mode="driving")
    minutes = result['rows'][0]['elements'][0]['duration']['value'] / 60
    # print('De: ', origem, ' para: ',destino, ' demora: ', minutes, 'minutos.')
    return minutes
'''

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

# def KNearest_Neighbors2(list_activities, cluster, workblock, k):
#     list_temp = []
#     for i in range(k):
#         nextIn = (float('inf'),None)
#         for clust in cluster:
#             for activity in list_activities:
#                 if (activity.state == 0) and (activity.appointment < workblock.finish) and (activity.appointment > workblock.start):
#                     distanceTemp = Distance_Calculator(activity.x, activity.y, clust.x, clust.y)
#                     if distanceTemp < nextIn[0]:
#                         nextIn = (distanceTemp,activity)
#         list_temp.append(nextIn[1])
#     return  list_temp
    
    


class KNearest_Nei:
    def __init__(self, atividade, distancia):
        """
        Inicializa a MinhaClasse com um atividade e a distancia ao trabalhador.

       
        Parameters
        ----------
        atividade: (Atividade)
            Atividade que esta a ser ponderada.
        distancia: (Double) 
            distancia em KM entre o local de partida do trabalhador e a atividade.
        """
        self.atividade = atividade
        self.distancia = distancia
    # se for menor tem de retornar true
    def __lt__(self, other):
        return self.distancia < other.distancia



def KNearest_Neighbors_Vote_in(atividade, workblock, skills):
    """
    Esta função verifica se a tarefa deve ser contada para o clustering do workblick ou não, verifica o estado da atividade, verifica o hora de marcação e se possiu as skills necessárias

    Parameters
    ----------
    kNearest_Nei: (KNearest_Nei)
        elemento a comparar com o bloco de trabalho para ver se entra.
    workblock: (WorkBlock)
        workblock que estamos a fazer o clustering das atividades para.
    skills: (list of str)
        lista das skills que o trabalhador possuiu.

    Returns
    -------
    tipo
        retorna True ou False, conforme se é para ser adicionada a lista ou não.
    """

    if atividade.appointment != time(0, 0):
  
        if (atividade.state != 1) and (atividade.appointment < workblock.finish) and (atividade.appointment > workblock.start) and (atividade.skill in skills):
            return True
   
    elif (atividade.state != 1) and (atividade.skill in skills):
        return True

    return False


def KNearest_Neighbors(list_activities, list_workers, workblock, k):
    distances = []
    worker = Find_Worker_By_Id(list_workers, workblock.idWorker)
    for activity in list_activities:
        distance = Distance_Calculator(activity.x, activity.y, workblock.x, workblock.y)
        distances.append(KNearest_Nei(activity, distance))

    distances = sorted(distances)
    
    list_temp = []
    count = 0
    indi = 0
    while count < k:
        if KNearest_Neighbors_Vote_in(distances[indi].atividade, workblock, worker.skill): # type: ignore
            list_temp.append(distances[indi].atividade)
            count += 1
        indi += 1
    return  list_temp




class Coordenada:
    def __init__(self, x, y):
        """
        Inicializa a MinhaClasse com um x e um y, que são as coordenadas.

       
        Parameters
        ----------
        x: (Int)
            coordenada do x.
        y: (Int) 
            coordendada do y.
        """
        self.x = x
        self.y = y

def KNearest_Neighbors2(list_activities, list_workers, workblock, k):
    """
    Esta função faz o clustering das atividades para o workblock.

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades a ponderar para o clustering.
    list_workers: (list of Workers)
        lista de todos os trabalhadores a ponderar para o clustering.
    workblock: (Workblock)
        workblock a ponderar para o clustering.
    k: (Int)
        quantidade de Atividades a colocar no cluster.

    Returns
    -------
    list of Activity
        Retorna uma lista de atividades, que é o cluster final.
    """

    # lista com os Atividades com a respetiva distancia
    distances = []

    # lista com as coordenadas dos elementos que já pertencem ao cluster
    list_coordenada_temp = []

    # lista com os elementes que já pertencem
    list_cluster = []

    # trabalhador que vai realizar este workblock
    worker = Find_Worker_By_Id(list_workers, workblock.idWorker)

    list_coordenada_temp.append(Coordenada(worker.x, worker.y)) # type: ignore
    for count in range(k):

        # colocar as atividades por ordem
        for activity in list_activities:

            # verificar se a atividade ainda não está a ser considerada.
            if activity.state == 0:
                for coord in list_coordenada_temp:
                    distance = Distance_Calculator(activity.x, activity.y, coord.x, coord.y)
                    if KNearest_Neighbors_Vote_in(activity, workblock, worker.skill): # type: ignore
                        distances.append(KNearest_Nei(activity, distance))
        
        distances = sorted(distances)
        atividade_in = distances[0].atividade
        atividade_in.state = 2 
        list_coordenada_temp.append(Coordenada(atividade_in.x, atividade_in.y)) # type: ignore
        list_cluster.append(atividade_in)
        distances.clear()

    return  list_cluster
    

def DBSCANS(list_activities, list_workers, work_Block, cluster, distance_Min, distance_Max, iterations_Max):
    
    min_x_value = float('inf')
    max_x_value = float('-inf')
    min_y_value = float('inf')
    max_y_value = float('-inf')

    worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

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
                        if distance < radius and (activity.appointment < work_Block.finish and activity.appointment > work_Block.start) and (activity.skill in worker.skill): # type: ignore
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
    plt.savefig('PNG_Graphics/HeatMapHours.png')
    plt.show(block = False)
    plt.close() 

'''
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
'''

def distancia(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def plot_activities_by_order(list_activities, nodes, work_Block):
    """
    Esta função representa num gráfico de pontos as atividades pertencentes ao cluster pela suas coordenadas, identifica com cores diferentes o trabalhador, as atividades atribuidas, e as atividades não atribuidas.
    Ainda coloca umas setas a mostrar o caminho percorrido pelo trabalhor.

    Parameters
    ----------
    list_activities: (lsit of Activity)
        atividades pertencentes ao cluster.
    nodes: (list of Node)
        lista de Node com as atividades que foram atribuidas pela ordem de atribuição.
    work_Block: (WorkBlock)
        lista das skills que o trabalhador possuiu.

    Returns
    -------
    null
        não retorna nada, só cria a imagem.
    """


    # lista só com os ids das atividades que vão ser realizadas, por ordem de realização
    activity_id_list = [node.id for node in nodes]

    x_values = []
    y_values = []
    points_colors = []

    # adicionar o ponto de partido do workblock ao gráfico 
    x_values.append(work_Block.x)
    y_values.append(work_Block.y)
    points_colors.append(0)

    # adicionar cada atividade ao gráfico 
    for num in activity_id_list:
        activity = Find_Activity_By_Id(list_activities, num)
        if activity:
            x_values.append(activity.x)
            y_values.append(activity.y)
            points_colors.append(3)

    # adicionar outra vez o workblock pois ao fim do dia ele volta
    x_values.append(work_Block.x)
    y_values.append(work_Block.y)
    points_colors.append(0)

    # Definir cores com base nos estados das tarefas
    colors = {0: 'black', 1: 'grey', 2: 'red', 3: 'green'} # aqui o 1: 'grey' nem é usado mas deixai o estar
    
    plt.figure(figsize=(15, 8))

    


    # adicionar cada seta para o percurso
    for i in range(len(x_values)-1):

        dx = x_values[i+1] - x_values[i]
        dy = y_values[i+1] - y_values[i]


        dist = distancia(x_values[i], y_values[i], x_values[i+1], y_values[i+1])

        # Ajustar o tamanho da cabeça da seta proporcionalmente à distância
        head_width = 0.08 * dist
        head_length = 0.08 * dist

        plt.arrow(x_values[i], y_values[i], dx, dy,
                color='blue', width=0.0005 * dist, head_width=head_width, head_length=head_length,length_includes_head=True)


    # adicionar as atividades que faltam ao gráfico
    for activity in list_activities:
        if activity.idActivity not in activity_id_list:
            x_values.append(activity.x)
            y_values.append(activity.y)
            points_colors.append(2)


    # passa o numero do state para uma  cor
    colors_order = [colors[color] for color in points_colors]
    

    '''

    criar o gráfico

    '''
    plt.scatter(x_values, y_values, c=colors_order)
    plt.title(str(work_Block.idWorker) + ' Start:' + str(work_Block.start)+ ' End:' + str(work_Block.finish))
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')

    legend_elements = [
        Line2D([], [], marker='o', color='green', label='Atribuídas', linestyle='None'),
        Line2D([], [], marker='o', color='black', label='Ponto de Partida', linestyle='None'),
        Line2D([], [], marker='o', color='red', label='Não Atribuídas', linestyle='None')
    ]
    
    for i, node in enumerate(nodes):
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            id = str(i) + ' |Id: ' + str(activity.idActivity)
            ap = '|Ap: ' + str(activity.appointment.hour) + ':' + str(activity.appointment.minute).zfill(2)
            travel = '|Tr: ' + str(int(node.travel_Time))
            start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
            end = '|End: ' + str(node.end_Time.hour) + ':' + str(node.end_Time.minute).zfill(2)
            skill = '|Sk: ' + activity.skill
            string =  id + ap + travel + start + end + skill
            legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
        
        else:
            if(i == 0):
                id = str(i) + ' |Id: ' + str(work_Block.idWorker)
                start = '|St: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
                string =  id + start
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
            else:
                id = str(i) + ' |Id: ' + str(work_Block.idWorker)
                end = '|End: ' + str(node.start_Time.hour) + ':' + str(node.start_Time.minute).zfill(2)
                travel = '|Tr: ' + str(int(node.travel_Time))
                string =  id + travel + end
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))

        

    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

    for activity in list_activities:
        if activity.idActivity not in activity_id_list:
            minute = str(activity.appointment.minute).zfill(2)
            hour = str(activity.appointment.hour)

            string = str(activity.idActivity) + ' | ' + hour + ':' + minute + ' | ' + activity.skill
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
    
    plt.savefig('PNG_Graphics/PlotMapState.png')
    plt.show(block = True)
    plt.close() 

