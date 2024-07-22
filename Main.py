# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

# from tkinter import N
from tkinter import N
import googlemaps
from datetime import datetime
from Activity import Activity
from Helper import pedir_s_n, printCadaOpcao, solicitar_input, importarAtividadesExcel, importarTrabalhadoresExcel, importarValoresExcel, preencherListaWorkBlocks, processarOpcao, Quantidade_Chamadas
from Workers import Worker
from Stats import DataAnalyticsByHour, DataAnalyticsBySkill, CalcularMediaQuantidadeAtividadesRealizadasPorTrabalhador, AnalisaTrabalhador, AnalisaTemposTrabalhadores
import pandas as pd
from Ploting import plot_heatmap_activities_by_hour, plot_activities_graph_by_state, plot_heatmap_activities_by_state
from dotenv import load_dotenv
import os


os.system("cls")

print("Deseja que seja considerada a prioridade das Atividades com marcação?")
considerarAgendamento = pedir_s_n()

print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
considerarPrioridade = pedir_s_n()

printCadaOpcao()
metodoCluster = solicitar_input(1, 5)

# Início da medição dos tempos
start_time = datetime.now()

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


activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
listaAtividades: list[Activity] = []
importarAtividadesExcel(activities_xlsx, listaAtividades)


workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore
listaTrabalhadores: list[Worker] = []
importarTrabalhadoresExcel(workers_xlsx, listaTrabalhadores)


values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
valoresTemp_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']
valores_dict = importarValoresExcel(valoresTemp_dict)


competencias_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
competencias_dict = competencias_xlsx.set_index('Skill').to_dict()['TimeActivity']


'''
    heat map por hora de marcação, mais escuro, mais tarde a hora de marcação
'''
plot_heatmap_activities_by_hour(listaAtividades)


listaBlocoTrabalho = preencherListaWorkBlocks(listaTrabalhadores)


processarOpcao(considerarAgendamento, considerarPrioridade, metodoCluster, gmaps, dicionario_distancias, listaAtividades, listaTrabalhadores, valores_dict, competencias_dict, listaBlocoTrabalho)

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

#print('\n\n Média: ', mediaQuantidadeAtividade, '\n')
#print('\n\n Limite: ', int(0.75 * mediaQuantidadeAtividade), '\n')

for trabalhador in listaTrabalhadores:
    if trabalhador.quantidadeAtividades < int(0.75 * mediaQuantidadeAtividade):
        AnalisaTrabalhador(trabalhador, listaAtividades, valores_dict)

AnalisaTemposTrabalhadores(listaTrabalhadores, listaAtividades, dicionario_distancias, valores_dict['tempoViagem1KM'], gmaps)
plot_heatmap_activities_by_state(listaAtividades)



'''
    printar o tempo de execução do programa
'''

print("Travel_Time foi chamada:", Quantidade_Chamadas() ,"vezes\n")
end_time = datetime.datetime.now() # type: ignore
elapsed_time = (end_time - start_time).total_seconds()
print("Tempo decorrido:", elapsed_time, "segundos")
