# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

# from tkinter import N
from tkinter import N
import googlemaps
import datetime
from Activity import Activity
from DBSCAN import *
from Workers import *
from Stats import *
import pandas as pd
from Ploting import *
from KNearest_Neighbors import *
from Central import *
from K_N_DBSCAN import *
from K_NearestNeighbors1 import *
from K_NearestNeighbors2 import *
import time
from dotenv import load_dotenv
import os

def main():

    print("Deseja que seja considerada a prioridade das Atividades com marcação?")
    considerarAgendamento = pedir_s_n()

    print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
    considerarPrioridade = pedir_s_n()

    # 1 - K-NearestNeighbors 1.0
    # 2 - K-NearestNeighbors 2.0
    # 3 - K-NearestNeighbors com DBSCANS
    # 4 - DBSCANS
    # 5 - Central

    print("Qual metodo de clustering deseja utilizar?\n1 - K-Nearest Neighbors (a comparar apenas ao ponto de partida)\n2 - K-Nearest Neighbors adapatado (a comparar a todos os elementos pertencentes ao cluster)\n3 - K-NearestNeighbors com DBSCANS (primeiro k nearest neighbors, depois o DBSCANS)\n4 - DBCANS (normal)\n5 - Central")
    metodoCluster = solicitar_input(1, 5)

    '''
        Configurar o Google Maps

    api_key = os.getenv("api_key") 
    print(api_key)
    gmaps = googlemaps.Client(key=api_key)
    '''
    
    gmaps = ''
    dicionario_distancias = {}
    
    '''
        ler dados do Excel
    '''
    # activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
    activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
    listaAtividades: list[Activity] = []
    for indice, element in activities_xlsx.iterrows():

        if element['ComprirAgendamento'] == 0:

            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
            # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
        else:
            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(), agendamento = datetime.datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))


    workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore
    listaTrabalhadores: list[Worker] = []

    for indice, element in workers_xlsx.iterrows():
        hours_str = element['HorarioTrabalho']
        hours_list = hours_str.split(',')
        tempo_listaBlocoTrabalho = []
        i = 0
        for hours in hours_list:
            start_hour, end_hour = hours.split(';')
            tempo_listaBlocoTrabalho.append(WorkBlock(element['idTrabalhador'], element['Longitude'], element['Latitude'], i,start_hour, end_hour))
            i += 1
        
        listaTrabalhadores.append(Worker(element['idTrabalhador'], element['Central'], [item.strip() for item in  element['skills'].split(',')]  , element['Longitude'], element['Latitude'], tempo_listaBlocoTrabalho))

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

    if metodoCluster == 1:
        Opcao_K_NearestNeighbors_Normal(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    elif metodoCluster == 2:
        Opcao_K_NearestNeighbors_Adaptado(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    elif metodoCluster == 3:
        Opcao_K_N_DBSCAN(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    elif metodoCluster == 4:
        Opcao_DBSCAN(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    elif metodoCluster == 5:
        Opcao_Agrupamento_Por_Central(listaAtividades, listaTrabalhadores, listaBlocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']), dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

    '''
        Análises estatísticas
    '''

    plot_activities_graph_by_state(listaAtividades)

    data = DataAnalyticsByHour(listaAtividades)
    sorted_stats_list = sorted(data)
    print('Atividades por hora agendamento (0 é sem agendamento):')
    for dat in sorted_stats_list:
        dat.print()

    data = DataAnalyticsBySkill(listaAtividades)
    print('\nAtividades por tipo de competencia:')
    for dat in data:
        dat.print()

    mediaQuantidadeAtividade = CalcularMediaQuantidadeAtividadesRealizadasPorTrabalhador(listaTrabalhadores)

    print('\n\n Média: ', mediaQuantidadeAtividade, '\n')
    print('\n\n Limite: ', int(0.75 * mediaQuantidadeAtividade), '\n')

    for trabalhador in listaTrabalhadores:
        if trabalhador.quantidadeAtividades < int(0.75 * mediaQuantidadeAtividade):
            AnalisaTrabalhador(trabalhador, listaAtividades, valores_dict)

    AnalisaTemposTrabalhadores(listaTrabalhadores, listaAtividades, dicionario_distancias, valores_dict['TRAVEL_TIME'], gmaps)
    plot_heatmap_activities_by_state(listaAtividades)




'''
    começar o "relógio" para o tempo de execução
'''

# Início da medição dos tempos
start_time = datetime.datetime.now()

os.system("cls")

'''
    printar o tempo de execução do programa
'''

main()
end_time = datetime.datetime.now() # type: ignore
elapsed_time = (end_time - start_time).total_seconds()
print("Tempo decorrido:", elapsed_time, "segundos")
print("Travel_Time foi chamada:", Quantidade_Chamadas() ,"vezes")
