# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

# from tkinter import N
import googlemaps
import datetime
from Activity import Activity
from DBSCANS import *
from Workers import *
from Stats import *
from Helper import Travel_Time
import pandas as pd
from Optimization import Greedy
from Ploting import *
from KNearest_Neighbors import *
from Central import *
from K_N_DBSCANS import *
from K_NearestNeighbors1 import *
from K_NearestNeighbors2 import *
import time
import timeit
from dotenv import load_dotenv
import os

'''

Configuração inicial da execução do código, 
definir as prioridades e o metodo de clustering

'''

def main():

    print("Deseja que seja considerada a prioridade das Atividades com marcação?")
    # considerarAgendamento = pedir_s_n()
    considerarAgendamento = False

    print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
    # considerarPrioridade = pedir_s_n()
    considerarPrioridade = False

    # 1 - K-NearestNeighbors 1.0
    # 2 - K-NearestNeighbors 2.0
    # 3 - K-NearestNeighbors com DBSCANS
    # 4 - DBSCANS
    # 5 - Central

    print("Qual metodo de clustering deseja utilizar?\n1 - K-Nearest Neighbors (a comparar apenas ao ponto de partida)\n2 - K-Nearest Neighbors adapatado (a comparar a todos os elementos pertencentes ao cluster)\n3 - K-NearestNeighbors com DBSCANS (primeiro k nearest neighbors, depois o DBSCANS)\n4 - DBCANS (normal)\n5 - Central")
    # metodoCluster = solicitar_input(1, 5)
    metodoCluster = 1

    '''

    Configurar o Google Maps

    api_key = os.getenv("api_key")
    print(api_key)
    gmaps = googlemaps.Client(key=api_key)

    '''
    gmaps = ''
    '''

    ler dados do Excel

    '''
    activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
    listaAtividades = []
    for indice, element in activities_xlsx.iterrows():

        if element['ComprirAgendamento'] == 0:

            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
            # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
        else:
            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(), agendamento = datetime.datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))
            # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude'], element['DataAgendamento'].to_pydatetime()))

    workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore
    listaTrabalhadores = []
    for indice, element in workers_xlsx.iterrows():
        hours_str = element['HorarioTrabalho']
        # print(hours_str)
        hours_list = hours_str.split(',')
        tempo_listaBlocoTrabalho = []
        i = 0
        for hours in hours_list:
            start_hour, end_hour = hours.split(';')
            tempo_listaBlocoTrabalho.append(WorkBlock(element['idTrabalhador'], element['Longitude'], element['Latitude'], i,start_hour, end_hour))
            i += 1
        
        listaTrabalhadores.append(Worker(element['idTrabalhador'], element['idCentral'], [item.strip() for item in  element['skills'].split(',')]  , element['Longitude'], element['Latitude'], tempo_listaBlocoTrabalho))

    values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
    valores_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']

    competencias_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
    competencias_dict = competencias_xlsx.set_index('Skill').to_dict()['TimeActivity']

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
        K_NearestNeighbors1(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)
        # cluster = KNearest_Neighbors1(listaAtividades, listaTrabalhadores, work_Block, int(valores_dict['K_NEAREST_NEIGHBORS1']))

    elif metodoCluster == 2:
        K_NearestNeighbors2(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)
        # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, int(valores_dict['K_NEAREST_NEIGHBORS1']))

    elif metodoCluster == 3:
        K_N_DBSCANS(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)
        # cluster = KNearest_Neighbors1(listaAtividades, listaTrabalhadores, work_Block, int(valores_dict['K_NEAREST_NEIGHBORS']))
        # cluster = DBSCANS(listaAtividades, listaTrabalhadores, work_Block, cluster, valores_dict['MIN_BDSCANS_DISTANCE'], valores_dict['MAX_BDSCANS_DISTANCE'], int(valores_dict['DBSCANS_IT_NUM']))

    elif metodoCluster == 4:
        print('Não funfa, ainda...')
        DBSCANS3(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    elif metodoCluster == 5:
        # print('Não funfa, ainda...')
        Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']), competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)
        # cluster = []
        # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, 10)
        # cluster = KNearest_Neighbors2(listaAtividades, listaTrabalhadores, work_Block, 10)








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

'''

começar o "relógio" para o tempo de execução

'''
start_time = datetime.datetime.now()

# Início da medição do tempo de CPU
start_time_cpu = time.process_time()

print('Começou')
'''

printar o tempo de execução do programa
'''
# Medir o tempo de CPU usando timeit

cpu_time_used = timeit.timeit(main, number=1)
print(f"Tempo timeit de CPU usado: {cpu_time_used} segundos")


end_time = datetime.datetime.now() # type: ignore
elapsed_time = (end_time - start_time).total_seconds()
print("Tempo decorrido:", elapsed_time, "segundos")

# Fim da medição do tempo de CPU
end_time_cpu = time.process_time()
# Tempo de CPU gasto
time_used = end_time_cpu - start_time_cpu
print(f"Tempo de CPU usado: {time_used} segundos")

print("Travel_Time foi chamada:", Quantidade_Chamadas() ,"vezes")