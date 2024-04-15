# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""
from Activity import Activity
from Activity import Find_Activity_By_Id
from Clustering import *
from Workers import *
import pandas as pd
from Optimization import Greedy

# Carregar os dados do arquivo Excel
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

        list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
    else: 
        list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento'].to_pydatetime()))


for indice, element in workers_xlsx.iterrows():
    hours_str = element['HorarioTrabalho']
    print(hours_str)
    hours_list = hours_str.split(',')
    print(hours_list)
    print(hours_list[0])
    tempo_list_work_blocks = []
    i = 0
    for hours in hours_list:
        print(hours)
        start_hour, end_hour = hours.split(';')
        tempo_list_work_blocks.append(WorkBlock(element['idTrabalhador'], element['xCasa'], element['yCasa'], i,start_hour, end_hour))
        i += 1
    
    list_workers.append(Worker(element['idTrabalhador'], element['idCentral'], element['codPostal'], element['skills'], element['xCasa'], element['yCasa'], tempo_list_work_blocks))

print('\nPrimeiros 5 Trabalhadores: \n')
for i in range(0, 5):
    if i < len(list_workers):
        list_workers[i].printWorker()

print('\nPrimeiras 5 Atividades: \n')
for i in range(0, 5):
    list_activities[i].printActivity() 

print('\nDados Importados com Sucesso!!\n')
plot_heatmap_activities(list_activities)


list_work_blocks = []
for worker in list_workers:
    for workBlock in worker.work_Blocks:
        list_work_blocks.append(workBlock)

for work_Block in list_work_blocks:

    cluster = KNearest_Neighbors(list_activities, work_Block.x, work_Block.y, int(values_dict['K_NEAREST_NEIGHBORS']))


    print("As 5 activities mais próximas:")
    for activity in cluster:
        activity.printActivity()


    DBSCANS(list_activities, work_Block, cluster, values_dict['MIN_BDSCANS_DISTANCE'], values_dict['MAX_BDSCANS_DISTANCE'], int(values_dict['DBSCANS_IT_NUM']))

    print("\n\nNovo Cluster:\n")
    print('Size: ', len(cluster))
    for activity in cluster:
        activity.printActivity()



    def activitiesToState1(nodes):
        for node in nodes:
            node.printNode()
            activity = Find_Activity_By_Id(list_activities, node.id)
            if activity:
                activity.state = 1

    nodes = Greedy(cluster, work_Block, skills_dict, list_workers, values_dict) 
    activitiesToState1(nodes)

    activity_id_list = [node.id for node in nodes]
    plot_activities_by_order(cluster, nodes, work_Block)

    for activity in list_activities:
        activity.resetStateToZeroIfNotOne()

print('Bora')