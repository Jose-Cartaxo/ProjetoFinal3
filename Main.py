# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""
from Activity import Activity
from Clustering import *
from Workers import *
import datetime
import pandas as pd

# Carregar os dados do arquivo Excel
workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKER') # type: ignore
activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
values_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

# Exibir os primeiros registros dos dados importados
print(workers_xlsx.head())
print(activities_xlsx.head())


# Horario Manhã
time_start_morning = datetime.time(8, 0, 0)
time_end_morning = datetime.time(12, 0, 0)

# Horario Tarde
time_start_aftermoon = datetime.time(13, 0, 0)
time_end_aftermoon = datetime.time(17, 0, 0)

print('Works Blocks: ')
work_block_morning = WorkBlock( '62764df6-b097-42b1-aa9c-65bf1c48ebc5', 1, time_start_morning, time_end_morning)
work_block_morning.printWorkBlock()
work_block_aftermoon = WorkBlock( '62764df6-b097-42b1-aa9c-65bf1c48ebc5', 2, time_start_aftermoon, time_end_aftermoon)
work_block_aftermoon.printWorkBlock()

list_work_blocks = [work_block_morning, work_block_aftermoon]

list_workers = []
list_activities = []

for indice, element in activities_xlsx.iterrows():
    if element['ComprirAgendamento'] == 0:

        list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
    else: 
        list_activities.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento']))

for indice, element in workers_xlsx.iterrows():
    list_workers.append(Worker(element['idTrabalhador'], element['idCentral'], element['codPostal'], element['skills'], element['xCasa'], element['yCasa'], list_work_blocks))

print('\nPrimeiros 5 Trabalhadores: \n')
for i in range(0, 5):
    if i < len(list_workers):
        list_workers[i].printWorker()

print('\nPrimeiras 5 Atividades: \n')
for i in range(0, 5):
    list_activities[i].printActivity() 

print('\nDados Importados com Sucesso!!\n')
plot_heatmap_activities(list_activities)

cluster = KNearest_Neighbors(list_activities, list_workers[1].x, list_workers[1].y, 5)

print("As 5 activities mais próximas:")
for activity in cluster:
    activity.printActivity()


DBSCANS(list_activities, list_workers[1].x, list_workers[1].y, cluster, values_dict['MIN_BDSCANS_DISTANCE'], values_dict['MAX_BDSCANS_DISTANCE'], int(values_dict['DBSCANS_IT_NUM']))

print("\n\nNovo Cluster:\n")
print('Size: ', len(cluster))
for activity in cluster:
    activity.printActivity()


for activity in cluster:
    list_workers[0].x