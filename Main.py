# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""
from Activity import Activity
from Clustering import KNearest_Neighbors
from Workers import *
import datetime
import pandas as pd

# Carregar os dados do arquivo Excel
workers_xlsx = pd.read_excel('WORKERS.xlsx')
activities_xlsx = pd.read_excel('ACTIVITIES.xlsx')

# Exibir os primeiros registros dos dados importados
print(workers_xlsx.head())
print(activities_xlsx.head())


# Horario Manhã
time_start_morning = datetime.time(8, 0, 0)
time_end_morning = datetime.time(12, 0, 0)

# Horario Tarde
time_start_aftermoon = datetime.time(14, 0, 0)
time_end_aftermoon = datetime.time(18, 0, 0)

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
    list_workers[i].printWorker()

print('\nPrimeiras 5 Atividades: \n')
for i in range(0, 5):
    list_activities[i].printActivity() 


print('Dados Importados com Sucesso!!')



activities_mais_proximas = KNearest_Neighbors(list_activities, list_workers[0].x, list_workers[0].y, 5)

print("As 5 activities mais próximas:")
for distancia, activity in activities_mais_proximas:
    print("Distância:", distancia)
    activity.printActivity() 