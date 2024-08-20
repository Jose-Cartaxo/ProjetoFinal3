from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from re import L
from matplotlib.pylab import f
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from Workers import BlocoTrabalho
from Activity import Atividade, Encontrar_Atividade_Por_Id
from Node import No

def distancia(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def plot_activities_by_order(list_activities: list[Atividade], nodes: list[No], work_Block: BlocoTrabalho) -> None:
    """Apresenta por ordem de realização, as atividades a serem realizadas pelo trabalhador, mostra ainda as atividades pertencentes ao cluster não atribuidas

    Args:
        list_activities (list[Atividade]): lista com as atividades do cluster
        nodes (list[No]): lista com os nós por ordem de realização
        work_Block (BlocoTrabalho): bloco de trabalho a que a atribuição foi realizada
    """


    # lista só com os ids das atividades que vão ser realizadas, por ordem de realização
    activity_id_list = [node.id for node in nodes]

    longitude_values = []
    latitude_values = []
    points_colors = []

    # adicionar o ponto de partido do workblock ao gráfico 
    longitude_values.append(work_Block.longitude)
    latitude_values.append(work_Block.latitude)
    points_colors.append(0)

    # adicionar cada atividade ao gráfico 
    for num in activity_id_list:
        activity = Encontrar_Atividade_Por_Id(list_activities, num)
        if activity:
            longitude_values.append(activity.longitude)
            latitude_values.append(activity.latitude)
            points_colors.append(3)

    # adicionar outra vez o workblock pois ao fim do dia ele volta
    longitude_values.append(work_Block.longitude)
    latitude_values.append(work_Block.latitude)
    points_colors.append(0)

    # Definir cores com base nos estados das tarefas
    colors = {0: 'black', 1: 'grey', 2: 'red', 3: 'green'} # aqui o 1: 'grey' nem é usado mas deixai o estar
    
    plt.figure(figsize=(15, 8))

    


    # adicionar cada seta para o percurso
    for i in range(len(longitude_values)-1):

        dx = longitude_values[i+1] - longitude_values[i]
        dy = latitude_values[i+1] - latitude_values[i]


        dist = distancia(longitude_values[i], latitude_values[i], longitude_values[i+1], latitude_values[i+1])

        # Ajustar o tamanho da cabeça da seta proporcionalmente à distância
        head_width = 0.08 * dist
        head_length = 0.08 * dist

        plt.arrow(longitude_values[i], latitude_values[i], dx, dy,
                color='blue', width=0.0005 * dist, head_width=head_width, head_length=head_length,length_includes_head=True)


    # adicionar as atividades que faltam ao gráfico
    for activity in list_activities:
        if activity.idAtividade not in activity_id_list:
            longitude_values.append(activity.longitude)
            latitude_values.append(activity.latitude)
            points_colors.append(2)


    # passa o numero do state para uma  cor
    colors_order = [colors[color] for color in points_colors]
    

    '''

    criar o gráfico

    '''
    plt.scatter(longitude_values, latitude_values, c=colors_order)
    plt.title(str(work_Block.idTrabalhador) + ' Start:' + str(work_Block.inicio)+ ' End:' + str(work_Block.fim) + ' Lucro: ' + str(nodes[-1].lucro_total))
    plt.xlabel('Longitude ')
    plt.ylabel('Latitude')

    legend_elements = [
        Line2D([], [], marker='o', color='green', label='Atribuídas', linestyle='None'),
        Line2D([], [], marker='o', color='black', label='Ponto de Partida', linestyle='None'),
        Line2D([], [], marker='o', color='red', label='Não Atribuídas', linestyle='None')
    ]
    
    for i, node in enumerate(nodes):
        activity = Encontrar_Atividade_Por_Id(list_activities, node.id)
        if activity:
            id = str(i) + ' |Id: ' + str(activity.idAtividade)
            ap = '|Ap: ' + str(activity.agendamento.hour) + ':' + str(activity.agendamento.minute).zfill(2)
            travel = '|Tr: ' + str(int(node.tempo_Viagem))
            start = '|St: ' + str(node.tempo_Inicio.hour) + ':' + str(node.tempo_Inicio.minute).zfill(2)
            end = '|End: ' + str(node.tempo_Fim.hour) + ':' + str(node.tempo_Fim.minute).zfill(2)
            skill = '|Sk: ' + activity.competencia
            string =  id + ap + travel + start + end + skill
            legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
        
        else:
            if(i == 0):
                id = str(i) + ' |Id: ' + str(work_Block.idTrabalhador)
                start = '|St: ' + str(node.tempo_Inicio.hour) + ':' + str(node.tempo_Inicio.minute).zfill(2)
                string =  id + start
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))
            else:
                id = str(i) + ' |Id: ' + str(work_Block.idTrabalhador)
                end = '|End: ' + str(node.tempo_Inicio.hour) + ':' + str(node.tempo_Inicio.minute).zfill(2)
                travel = '|Tr: ' + str(int(node.tempo_Viagem))
                string =  id + travel + end
                legend_elements.append(Line2D([], [], marker='o', color='white', label=string))

        

    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

    for activity in list_activities:
        if activity.idAtividade not in activity_id_list:
            minute = str(activity.agendamento.minute).zfill(2)
            hour = str(activity.agendamento.hour)

            string = str(activity.idAtividade) + ' | ' + hour + ':' + minute + ' | ' + activity.competencia
            plt.text(activity.longitude, activity.latitude, string, fontsize=8, ha='right', va='bottom')

    plt.tight_layout()
    path = 'PNG_Graphics/' + str(work_Block.idTrabalhador) + 'Block' + str(work_Block.idBloco) + '.png'
    
    plt.savefig(path)
    # plt.show(block=False)
    # plt.show(block=True)
    plt.close() 
    return



def plot_activities_graph_by_state(list_activities: list[Atividade]):
    list_states = [0,0]
    for activity in list_activities:
        list_states[activity.estado] = list_states[activity.estado] + 1 
    

    indices = range(len(list_states))

    # Criar o gráfico de barras
    plt.bar(indices, list_states)

    # Adicionar rótulos aos eixos
    plt.xlabel('Estado')
    plt.ylabel('Quantidade')

    # Adicionar título ao gráfico
    plt.title('Gráfico Quantidade por Estado')

    # Adicionar rótulos às barras
    for i, valor in enumerate(list_states):
        plt.text(i, valor, str(valor), ha='center', va='bottom')

    # Definir os ticks do eixo x com rótulos personalizados
    plt.xticks(indices, ['Não Atribuídas', 'Atribuídas'])

    #Salvar e fechar
    plt.savefig('PNG_Graphics/GráficoBarrasQuantidadePorEstado.png')
    plt.close() 

    # Rótulos para os setores
    labels = ['Não Atribuídas', 'Atribuídas']

    # Cores para os setores
    colors = ['#b32e2e','#2eb34d']

    # Criar o gráfico de pizza
    plt.pie(list_states, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)

    # Adicionar título ao gráfico
    plt.title('Gráfico Quantidade por Estado')

    # Salvar o gráfico como um arquivo PNG
    plt.savefig('PNG_Graphics/GráficoCircularQuantidadePorEstado.png')
    plt.close()



def plot_heatmap_activities_by_state(list_activities: list[Atividade]):
    # Extrair coordenadas x, y e timestamps
    longitude_values = [task.longitude for task in list_activities]
    latitude_values = [task.latitude for task in list_activities]
    timestamps = [task.estado for task in list_activities]

    # Converter timestamps para valores numéricos para representar as cores
    # Por exemplo, você pode usar a hora do timestamp como o valor da cor
    color_values = [timestamp for timestamp in timestamps]

    # Criar heatmap
    plt.figure(figsize=(8, 6))
    heatmap = plt.scatter(longitude_values, latitude_values, c=color_values, cmap='viridis', s=100, alpha=0.7)
    plt.colorbar(heatmap, label='State')
    plt.title('Heatmap das Atividades por State')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Mostrar o heatmap
    plt.savefig('PNG_Graphics/HeatMapState.png')
    plt.show()



def plot_heatmap_activities_by_hour(list_activities: list[Atividade]) -> None:
    """Faz um Heatmap com todas as atividades no seu local geográfico, a cor de cada ponto do heat map representa a sua hora de agendamento

    Args:
        list_activities (list[Atividade]): Lista com todas as atividades a serem representadas no Heatmap
    """
    # Extrair coordenadas x, y e timestamps
    longitude_values = [task.longitude for task in list_activities]
    latitude_values = [task.latitude for task in list_activities]
    timestamps = [task.agendamento.hour for task in list_activities]

    # Converter timestamps para valores numéricos para representar as cores
    # Por exemplo, você pode usar a hora do timestamp como o valor da cor
    color_values = [timestamp for timestamp in timestamps]

    # Criar heatmap
    plt.figure(figsize=(8, 6))
    heatmap = plt.scatter(longitude_values, latitude_values, c=color_values, cmap='viridis', s=100, alpha=0.7)
    plt.colorbar(heatmap, label='Hora da Marcação')
    plt.title('Heatmap das Atividades')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Mostrar o heatmap
    plt.savefig('PNG_Graphics/HeatMapHours.png')
    # plt.show(block = False)
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

 # Função auxiliar para criar o gráfico de dispersão com linha de tendência
def create_scatter_plot_with_trendline(x, y, title, filename):
    # Criando o gráfico de dispersão
    plt.scatter(x, y)

    # Calculando a linha de tendência
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), linestyle='-', color='r')

    # Adicionando rótulos aos eixos
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')

    # Adicionando título ao gráfico
    plt.title(title)

    # Exibindo e salvando o gráfico
    plt.grid(True)
    plt.savefig(filename)
    # plt.show()
    plt.close() 

def plot_scatter_with_trendline(dados):
    # Separando os dados em listas separadas para o eixo x e y
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for stat in dados:
        if stat.tipo == 'manha':
            x1.append(stat.id)
            y1.append(stat.quantidade)
        else:
            x2.append(stat.id)
            y2.append(stat.quantidade)

    # Criando o gráfico de dispersão com linha de tendência para a manhã
    create_scatter_plot_with_trendline(x1, y1, 'Gráfico de Dispersão com Linha de Tendência - Manhã', 'PNG_Graphics/PlotTrendline_Manha.png')

    # Criando o gráfico de dispersão com linha de tendência para a tarde
    create_scatter_plot_with_trendline(x2, y2, 'Gráfico de Dispersão com Linha de Tendência - Tarde', 'PNG_Graphics/PlotTrendline_Tarde.png')