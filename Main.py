# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

from tkinter import N
import googlemaps
import datetime
from Activity import Activity
from DBSCANS import *
from Workers import *
from Stats import *
from Helper import *
import pandas as pd
from Optimization import Greedy
from Ploting import *
from KNearest_Neighbors import *
from Central import *

'''

Configuração inicial da execução do código, 
definir as prioridades e o metodo de clustering

'''


print("Deseja que seja considerada a prioridade das Atividades com marcação?")
# considerAppointment = pedir_s_n()
considerAppointment = False

print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
# considerPriority = pedir_s_n()
considerPriority = False

# 1 - K-NearestNeighbors 1.0
# 2 - K-NearestNeighbors 2.0
# 3 - K-NearestNeighbors com DBSCANS
# 4 - DBSCANS
# 5 - Central

print("Qual metodo de clustering deseja utilizar?\n1 - K-Nearest Neighbors (a comparar apenas ao ponto de partida)\n2 - K-Nearest Neighbors adapatado (a comparar a todos os elementos pertencentes ao cluster)\n3 - K-NearestNeighbors com DBSCANS (primeiro k nearest neighbors, depois o DBSCANS)\n4 - DBCANS (normal)\n5 - Central")
# metodoCluster = solicitar_input(1, 5)
metodoCluster = 5
'''

Configurar o Google Maps

'''
api_key = 'AIzaSyB_brs6KxO_ZbAzviY4L2pzlE1wgY0VaQg'
# Inicialize o cliente da API do Google Maps
gmaps = googlemaps.Client(key=api_key)

'''

começar o "relógio" para o tempo de execução

'''
start_time = datetime.now()

'''

ler dados do Excel

'''
activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
listaAtividades = []
for indice, element in activities_xlsx.iterrows():

    if element['ComprirAgendamento'] == 0:

        listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
        # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
    else:
        listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(),appointment = datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))
        # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento'].to_pydatetime()))

workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKER') # type: ignore
listaTrabalhadores = []
for indice, element in workers_xlsx.iterrows():
    hours_str = element['HorarioTrabalho']
    print(hours_str)
    hours_list = hours_str.split(',')
    tempo_listaBlocoTrabalho = []
    i = 0
    for hours in hours_list:
        start_hour, end_hour = hours.split(';')
        tempo_listaBlocoTrabalho.append(WorkBlock(element['idTrabalhador'], element['xCasa'], element['yCasa'], i,start_hour, end_hour))
        i += 1
    
    listaTrabalhadores.append(Worker(element['idTrabalhador'], element['idCentral'], element['codPostal'],  [item.strip() for item in  element['skills'].split(',')]  , element['xCasa'], element['yCasa'], tempo_listaBlocoTrabalho))

values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
values_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

skills_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
skills_dict = skills_xlsx.set_index('Skill').to_dict()['TimeActivity']

'''

heat map por hora de marcação, mais escuro, mais tarde a hora de marcação

'''

plot_heatmap_activities_by_hour(listaAtividades)

'''

Fazer uma lista só com os workblocks para se irem adicionamdo as atividades a estes

'''

listaBlocoTrabalho = []
for worker in listaTrabalhadores:
    for workBlock in worker.work_Blocks:
        listaBlocoTrabalho.append(workBlock)


list_worker_activityQuantity = [] # lista onde para cada workblock é colocada a quantidade de atividades realizadas nesse workblock

























'''

correr o programa com o método de clustering escolhido

'''

# 1 - K-NearestNeighbors 1.0
# 2 - K-NearestNeighbors 2.0
# 3 - K-NearestNeighbors com DBSCANS
# 4 - DBSCANS
# 5 - Central

cluster = []

if metodoCluster == 1:
    print('Não funfa, ainda...')
    # cluster = KNearest_Neighbors1(listaAtividades, listaTrabalhadores, work_Block, int(values_dict['K_NEAREST_NEIGHBORS1']))

elif metodoCluster == 2:
    print('Não funfa, ainda...')
    # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, int(values_dict['K_NEAREST_NEIGHBORS1']))

elif metodoCluster == 3:
    print('Não funfa, ainda...')
    # cluster = KNearest_Neighbors1(listaAtividades, listaTrabalhadores, work_Block, int(values_dict['K_NEAREST_NEIGHBORS']))
    # cluster = DBSCANS(listaAtividades, listaTrabalhadores, work_Block, cluster, values_dict['MIN_BDSCANS_DISTANCE'], values_dict['MAX_BDSCANS_DISTANCE'], int(values_dict['DBSCANS_IT_NUM']))

elif metodoCluster == 4:
    print('Não funfa, ainda...')
    # cluster = DBSCANS2(listaAtividades, listaTrabalhadores, work_Block, values_dict['MIN_BDSCANS_DISTANCE'], int(values_dict['DBSCANS_IT_NUM']))

elif metodoCluster == 5:
    # print('Não funfa, ainda...')
    cluster = Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, int(values_dict['K_NEAREST_NEIGHBORS']))
    # cluster = []
    # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, 10)
    # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, 10)



# if len(cluster) != 0:
#     nodes = Greedy(cluster, work_Block, skills_dict, listaTrabalhadores, values_dict, considerAppointment, considerPriority, gmaps)












# '''

# colocar as atividades que foram atribuidas com o state == 1
# '''
# activitiesToState1(nodes, listaAtividades)

# '''

# fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock
# '''
# plot_activities_by_order(cluster, nodes, work_Block)

# '''

# colocar todas as atividades que não têm o state igual a 1 a 0
# '''
# for activity in listaAtividades:
#     activity.resetStateToZeroIfNotOne()


# '''

# fazer um gráfico com a evolução da atribuição das atividades
# '''
# activityQuantity = len(nodes) - 2

# meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
# if work_Block.start < meio_dia:
#     list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
# else:
#     list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))





















'''

printar o tempo de execução do programa
'''
end_time = datetime.now() # type: ignore
elapsed_time = end_time - start_time
print("Tempo decorrido:", elapsed_time, "segundos")


'''

Análises estatísticas
'''
plot_activities_graph_by_state(listaAtividades)

plot_heatmap_activities_by_state(listaAtividades)

data = DataAnalyticsByHour(listaAtividades)
sorted_stats_list = sorted(data)
for dat in sorted_stats_list:
    dat.print()

data = DataAnalyticsBySkill(listaAtividades)

for dat in data:
    dat.print()



print(type(data[0].tipo))
plot_scatter_with_trendline(list_worker_activityQuantity)

