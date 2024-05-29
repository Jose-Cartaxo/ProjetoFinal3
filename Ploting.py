from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from re import L

from matplotlib.pylab import f
from Workers import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from Activity import *

def distancia(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def plot_activities_by_order(list_activities, nodes, work_Block: WorkBlock):
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
    x_values.append(work_Block.longitude)
    y_values.append(work_Block.latitude)
    points_colors.append(0)

    # adicionar cada atividade ao gráfico 
    for num in activity_id_list:
        activity = Find_Activity_By_Id(list_activities, num)
        if activity:
            x_values.append(activity.longitude)
            y_values.append(activity.latitude)
            points_colors.append(3)

    # adicionar outra vez o workblock pois ao fim do dia ele volta
    x_values.append(work_Block.longitude)
    y_values.append(work_Block.latitude)
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
            x_values.append(activity.longitude)
            y_values.append(activity.latitude)
            points_colors.append(2)


    # passa o numero do state para uma  cor
    colors_order = [colors[color] for color in points_colors]
    

    '''

    criar o gráfico

    '''
    plt.scatter(x_values, y_values, c=colors_order)
    plt.title(str(work_Block.idWorker) + ' Start:' + str(work_Block.inicio)+ ' End:' + str(work_Block.fim))
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
            skill = '|Sk: ' + activity.competencia
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

            string = str(activity.idActivity) + ' | ' + hour + ':' + minute + ' | ' + activity.competencia
            plt.text(activity.longitude, activity.latitude, string, fontsize=8, ha='right', va='bottom')

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



def plot_heatmap_activities_by_state(list_activities):
    # Extrair coordenadas x, y e timestamps
    x_values = [task.longitude for task in list_activities]
    y_values = [task.latitude for task in list_activities]
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
    x_values = [task.longitude for task in list_activities]
    y_values = [task.latitude for task in list_activities]
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
