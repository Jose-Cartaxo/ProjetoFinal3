from Main import main
import pandas as pd

# Caminho para o arquivo Excel existente
caminho_arquivo = 'ResultadosCU.xlsx'


metodoCluster = 1
dbscan_min = -1
dbscan_max = -1
dbscan_ite = -1
knn_ite = 1
tempo_dep = 1
tempo_ant = 1
res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
Percent_Atividades = res[0]
Quant_Pdd = res[1]
Quant_No = res[2]

novos_dados = {
    'metodoClustering': metodoCluster,
    'dbscan_min': dbscan_min,
    'dbscan_max': dbscan_max,
    'dbscan_ite': dbscan_ite,
    'knn_ite': knn_ite,
    'tempo_dep': tempo_dep,
    'tempo_ant': tempo_ant,
    'Percent Atividades': Percent_Atividades,
    'Quant Pdd': Quant_Pdd,
    'Quant No': Quant_No
}


# Carregar o arquivo Excel existente
df = pd.read_excel(caminho_arquivo)

# Criar um DataFrame com a nova linha
df_novos_dados = pd.DataFrame([novos_dados])

# Concatenar o DataFrame existente com o DataFrame da nova linha
df = pd.concat([df, df_novos_dados], ignore_index=True)

# Salvar o arquivo Excel
df.to_excel(caminho_arquivo, index=False)


"""
MetodoClustering	dbscan_min	dbscan_max	dbscan_ite	knn_ite	tempo_dep	tempo_ant	Percent Atividades
Quant Pdd	Quant No
"""


'''
workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')  # type: ignore
first_row = workers_xlsx.iloc[0]


id = first_row['NUMINT']
print(type(id))

central = first_row['Central']
print(type(central))

longitude = first_row['Longitude']
print(type(longitude))

lorena = datetime.datetime.strptime(first_row['DataCriacao'], '%d/%m/%y').date()
print(type(lorena))


values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
valores_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

print('Valores dicionário valores_dict:')
pprint(valores_dict)

'''
'''
skills_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
skills_dict = skills_xlsx.set_index('Skill').to_dict()['TimeActivity']

print('Valores dicionário skills_dict:')
pprint(skills_dict)

'''
'''
class Atividade:
    # Esta é uma classe de exemplo para representar a atividade
    def __init__(self, nome):
        self.nome = nome

class KNearest_Nei:
    def __init__(self, atividade, distancia):
        """
        Inicializa a MinhaClasse com uma atividade e a distancia ao trabalhador.

        Parameters
        ----------
        atividade: (Atividade)
            Atividade que está sendo ponderada.
        distancia: (float)
            Distância em KM entre o local de partida do trabalhador e a atividade.
        """
        self.atividade = atividade
        self.distancia = distancia

    # se for menor tem de retornar true
    def __lt__(self, other):
        return self.distancia < other.distancia

# Criando uma lista de objetos KNearest_Nei para exemplo
atividade1 = Atividade("Atividade 1")
atividade2 = Atividade("Atividade 2")
atividade3 = Atividade("Atividade 3")

lista_de_atividades = [
    KNearest_Nei(atividade1, 10.0),
    KNearest_Nei(atividade2, 5.0),
    KNearest_Nei(atividade3, 8.0)
]

# Encontre o menor elemento com base na distância
menor_elemento = min(lista_de_atividades)

# O menor_elemento agora é o objeto KNearest_Nei com a menor distância
print(f"A atividade com a menor distância é: {menor_elemento.atividade.nome}")
print(f"A distância é: {menor_elemento.distancia} km")




import googlemaps
import gmplot
from datetime import datetime

api_key = 'AIzaSyB_brs6KxO_ZbAzviY4L2pzlE1wgY0VaQg'

# Inicialize o cliente da API do Google Maps
def generate_google_maps_link(start, waypoints, destination):
    base_url = "https://www.google.com/maps/dir/?api=1"
    start_str = f"origin={start[0]},{start[1]}"
    destination_str = f"destination={destination[0]},{destination[1]}"
    waypoints_str = "&waypoints=".join([f"{coord[0]},{coord[1]}" for coord in waypoints])
    return f"{base_url}&{start_str}&{waypoints_str}&{destination_str}"

# Exemplo de coordenadas (latitude, longitude)
ponto_partida = (40.05298780198781, -7.54346237602345)  # São Paulo, Brasil
destino = (42.75578749461006, 1.6430955325487684)           # Paris, França
pontos_intermediarios = [
    (37.71520740124046, -4.766190413644785)  # Rio de Janeiro, Brasil
]

link = generate_google_maps_link(ponto_partida, pontos_intermediarios, destino)
print(link)

'''
# https://www.google.com/maps/dir/40.0529878,-7.5434624/37.71520740124046,4.766190413644785/42.7557875,1.6430955/

# https://www.google.com/maps/dir/40.0529878,-7.5434624/37.71520740124046,+-4.766190413644785/42.7557875,1.6430955/@40.076335,-8.1972655,6z/data=!3m1!4b1!4m8!4m7!1m0!1m3!2m2!1d-4.7661904!2d37.7152074!1m0!3e0?entry=ttu

'''
workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore

activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')

values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
values_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

skills_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
skills_dict = skills_xlsx.set_index('Skill').to_dict()['TimeActivity']




# Exibir os primeiros registros dos dados importados
# print(workers_xlsx.head())
# print(activities_xlsx.head())



# tempo_list_work_blocks = Create_List_Work_Blocks()

list_workers = []
list_activities = []

for indice, element in activities_xlsx.iterrows():

    if element['ComprirAgendamento'] == 0:

        list_activities.append(Activity(id = element['NUMINT'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
        # list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
    else:

        list_activities.append(Activity(id = element['NUMINT'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(),appointment = datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))
        # list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento'].to_pydatetime()))


for indice, element in workers_xlsx.iterrows():
    hours_str = element['HorarioTrabalho']
    # print(hours_str)
    hours_list = hours_str.split(',')
    # print(hours_list)
    # print(hours_list[0])
    tempo_list_work_blocks = []
    i = 0
    for hours in hours_list:
        # print(hours)
        start_hour, end_hour = hours.split(';')
        tempo_list_work_blocks.append(WorkBlock(element['idTrabalhador'], element['xCasa'], element['yCasa'], i,start_hour, end_hour))
        i += 1
    
    list_workers.append(Worker(element['idTrabalhador'], element['idCentral'], element['codPostal'], element['skills'], element['xCasa'], element['yCasa'], tempo_list_work_blocks))

while True:
    worker = input('Numero do Worker: ')
    activity = input('Numero da Atividade: ')
    # worker = 'id-' + worker
    worker = 'Worker-' + worker
    activity = 'id-' + activity

    activityVar1 = Find_Activity_By_Id(list_activities, worker)
    if not activityVar1:
        activityVar1 = Find_Worker_By_Id(list_workers, worker)
    activityVar2 = Find_Activity_By_Id(list_activities, activity)
    print(Travel_Time( activityVar1.x, activityVar1.y, activityVar2.x, activityVar2.y, gmaps))
'''

'''
# WORKER 1

# travel_Time_Returning = Travel_Time(1.1, activity.x, activity.y, workBlock.x, workBlock.y)
travel_Time_Going = Travel_Time(1.1, 46.6429571, -0.245801, 46.61595329435522, -0.210348095870298)
print(travel_Time_Going)
# travel_Time_Returning = Travel_Time(1.1, activity.x, activity.y, workBlock.x, workBlock.y)
travel_Time_Going = Travel_Time(1.1, 46.6427645, -0.2239158, 46.61595329435522, -0.210348095870298)
print(travel_Time_Going)

no = Node(0,0,0,0,0,None)

frontier = []
heapq.heappush(frontier, Node(1, 1, 0,0, 0, no))
heapq.heappush(frontier, Node(2, 3, 0,0, 0, no))
heapq.heappush(frontier, Node(3, 2, 0,0, 0, no))
heapq.heappush(frontier, Node(4, 4, 0,0, 0, no))
heapq.heappush(frontier, Node(5, 5, 0,0, 0, no))
frontier = sorted(frontier)
for fr in frontier:
    print(fr.id)

'''
# cost = CostCalculator(travel_Time_Going, travel_Time_Going, 25, values_dict)

"""

import openpyxl
from random import uniform

# Carregue o arquivo Excel
workbook = openpyxl.load_workbook('WORKERS.xlsx')

# Selecione a planilha desejada
sheet = workbook['WORKERS']

# Itere sobre as células na coluna em que deseja adicionar os valores aleatórios
for cell in sheet['F']:
    # Verifique se a célula não é a primeira linha (cabeçalho)
    if cell.row != 1:
        # Obtenha o valor atual da célula
        valor_atual = cell.value
        # Se o valor existente não for None, adicione um valor aleatório entre -0.1 e 0.1
        if valor_atual is not None:
            valor_aleatorio = uniform(-0.1, 0.1)
            novo_valor = valor_atual + valor_aleatorio
            # Escreva o novo valor de volta na célula
            cell.value = novo_valor

# Salve as alterações no arquivo Excel
workbook.save('WORKERS2.xlsx')

"""

"""

from Clustering import *

print(Travel_Time( 1.1, 44.2747947, 0.5920027, 44.328734, 0.5913167))

print(Travel_Time( 1.1, 44.3, 0.6, 44.328734, 0.5913167))

"""


"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Seus dados de pontos e cores
x_values = [1, 2, 3, 4, 5]
y_values = [2, 3, 4, 5, 6]
cores_pontos = ['red', 'black', 'green', 'blue', 'orange']

# Definindo coordenadas de início e fim dos vetores
x_start = [1, 2, 3]  # coordenadas x do ponto inicial
y_start = [2, 3, 4]  # coordenadas y do ponto inicial
x_end = [2, 3, 4]    # coordenadas x do ponto final
y_end = [3, 4, 5]    # coordenadas y do ponto final
cores_vetores = ['black', 'blue', 'green']  # cores dos vetores

# Plotando o gráfico de dispersão
plt.scatter(x_values, y_values, c=cores_pontos)
plt.title('Gráfico de Coordenadas das Tarefas')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')

# Adicionando os vetores ao gráfico
for i in range(len(x_start)):
    plt.arrow(x_start[i], y_start[i], x_end[i] - x_start[i], y_end[i] - y_start[i],
              color=cores_vetores[i], width=0.05, head_width=0.3, length_includes_head=True)

# Adicionando legenda
legend_elements = [
    Line2D([], [], marker='o', color='red', label='Não contabilizadas', linestyle='None'),
    Line2D([], [], marker='o', color='black', label='Ponto Partida', linestyle='None'),
    Line2D([], [], marker='o', color='green', label='Contabilizadas', linestyle='None'),
    Line2D([], [], marker='o', color='blue', label='Atribuidas', linestyle='None'),
    Line2D([], [], color='black', linewidth=1, label='Vetores')
]

plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

# Exibindo o gráfico
plt.show()

"""


'''

import heapq

class Node:
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value > other.value  # Retornar True se o valor de self for maior que o valor de other

lista = []
node1 = Node(10)
node2 = Node(20)
heapq.heappush(lista, node1)
heapq.heappush(lista, node2)

current_Node = heapq.heappop(lista)


print(current_Node.value)  

'''

