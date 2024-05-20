# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

import googlemaps
import datetime
from Activity import Activity
from Activity import Find_Activity_By_Id
from Clustering import *
from Workers import *
from Stats import *
from Helper import *
import pandas as pd
from Optimization import Greedy

'''

Configuração inicial da execução do código, 
definir as prioridades e o metodo de clustering

'''


print("Deseja que seja considerada a prioridade das Atividades com marcação?")
considerAppointment = pedir_s_n()

print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
considerPriority = pedir_s_n()

print("Qual metodo de clustering deseja utilizar? \n1 - K-Nearest Neighbors (a comparar apenas ao ponto de partida) \n2 - K-Nearest Neighbors adapatado (a comparar a todos os elementos pertencentes ao cluster) \n3 - K-NearestNeighbors com DBSCANS (primeiro k nearest neighbors, depois o DBSCANS) \n 4 - DBCANS (normal) \n5 - CodPostal \n6 - Central")
metodoCluster = solicitar_input(1, 6)

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
list_activities = []
for indice, element in activities_xlsx.iterrows():

    if element['ComprirAgendamento'] == 0:

        list_activities.append(Activity(id = element['NUMINT'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
        # list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
    else:
        list_activities.append(Activity(id = element['NUMINT'], skill = element['Skill'], x = element['Latitude'], y = element['Longitude'], creation = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(),appointment = datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))
        # list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento'].to_pydatetime()))

workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKER') # type: ignore
list_workers = []
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
    
    list_workers.append(Worker(element['idTrabalhador'], element['idCentral'], element['codPostal'],  [item.strip() for item in  element['skills'].split(',')]  , element['xCasa'], element['yCasa'], tempo_list_work_blocks))

values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
values_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

skills_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
skills_dict = skills_xlsx.set_index('Skill').to_dict()['TimeActivity']



'''

a seguir seriam uns prints a mostrar que os valores foram bem importados

'''

'''
print('\nPrimeiros 5 Trabalhadores: \n')
for i in range(0, 5):
    if i < len(list_workers):
        list_workers[i].printWorker()

print('\nPrimeiras 5 Atividades: \n')
for i in range(0, 5):
    list_activities[i].printActivity() 

print('\nDados Importados com Sucesso!!\n')
'''

'''

heat map por hora de marcação, mais escuro, mais tarde a hora de marcação

'''
'''

plot_heatmap_activities_by_hour(list_activities)

'''

'''

Fazer uma lista só com os workblocks para se irem adicionamdo as atividades a estes

'''

list_work_blocks = []
for worker in list_workers:
    for workBlock in worker.work_Blocks:
        list_work_blocks.append(workBlock)


list_worker_activityQuantity = [] # lista onde para cada workblock é colocada a quantidade de atividades realizadas nesse workblock
for work_Block in list_work_blocks:

    cluster = KNearest_Neighbors2(list_activities, list_workers, work_Block, 10)
    '''

    cluster = KNearest_Neighbors(list_activities, list_workers, work_Block, int(values_dict['K_NEAREST_NEIGHBORS']))
    DBSCANS(list_activities, list_workers, work_Block, cluster, values_dict['MIN_BDSCANS_DISTANCE'], values_dict['MAX_BDSCANS_DISTANCE'], int(values_dict['DBSCANS_IT_NUM']))

    '''

    def activitiesToState1(nodes):
        for node in nodes:
            activity = Find_Activity_By_Id(list_activities, node.id)
            if activity:
                activity.state = 1

    nodes = Greedy(cluster, work_Block, skills_dict, list_workers, values_dict, considerAppointment, considerPriority, gmaps) 
    activitiesToState1(nodes)

    plot_activities_by_order(cluster, nodes, work_Block)

    for activity in list_activities:
        activity.resetStateToZeroIfNotOne()
    
    activityQuantity = len(nodes) - 2

    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    if nodes[0].start_Time.time() < meio_dia:
        list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
    else:
        list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))

end_time = datetime.now() # type: ignore
elapsed_time = end_time - start_time
print("Tempo decorrido:", elapsed_time, "segundos")

for skill in list_workers[0].skill:
    print('Skil: ', skill,'\n')


plot_activities_graph_by_state(list_activities)

plot_heatmap_activities_by_state(list_activities)

data = DataAnalyticsByHour(list_activities)
sorted_stats_list = sorted(data)
for dat in sorted_stats_list:
    dat.print()

data = DataAnalyticsBySkill(list_activities)
for dat in data:
    dat.print()



print(type(data[0].tipo))
plot_line_graph(list_worker_activityQuantity)

