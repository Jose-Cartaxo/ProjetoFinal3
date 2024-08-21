# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""

# from tkinter import N
from tkinter import N
import googlemaps
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd

from Activity import Atividade

from Helper import importar_Atividades_Excel, importar_Trabalhadores_Excel, importar_Valores_Excel, preencherListaWorkBlocks, Quantidade_Chamadas, limpar_pasta

from Printer import printCadaOpcao, processarOpcao, pedir_s_n, solicitar_input

from Workers import BlocoTrabalho, Trabalhador

from Stats import AnalisaDadosPorSkill, AnalisaDadosPorHora, CalcularMediaQuantidadeAtividadesRealizadasPorTrabalhador, AnalisaTrabalhador, AnalisaTemposTrabalhadores


from Ploting import plot_heatmap_activities_by_hour, plot_activities_graph_by_state, plot_heatmap_activities_by_state

from Node import No



os.system("cls")

print("Deseja que seja considerada a prioridade das Atividades com marcação?")
considerarAgendamento: bool = pedir_s_n()
"""Bool com a informação de é para considerar a prioridade no agendamento ou não"""

print("Deseja que seja considerada a prioridade das Atividades com menor data de criação?")  
considerarPrioridade: bool = pedir_s_n()
"""Bool com a informação de é para considerar a prioridade na data de criação ou não"""

printCadaOpcao()
metodoCluster: int = solicitar_input(1, 5)
"""Método de clustering escolhido"""

limpar_pasta("TXT_Logs")
limpar_pasta("PNG_Graphics")

# Início da medição dos tempos
start_time: datetime = datetime.now()

'''
    Configurar o Google Maps

api_key = os.getenv("api_key") 
print(api_key)
gmaps = googlemaps.Client(key=api_key)
'''

gmaps = ''

# dicuinário coma s distâncias já calculadas
dicionario_distancias: dict = {}

# ler dados do Excel
activities_xlsx: pd.DataFrame = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
listaAtividades: list[Atividade] = []
"""Lista com todas as atividades do Excel importadas"""
importar_Atividades_Excel(activities_xlsx, listaAtividades)


workers_xlsx: pd.DataFrame  = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore
listaTrabalhadores: list[Trabalhador] = []
"""Lista com todos os trabalhadores do Excel"""
importar_Trabalhadores_Excel(workers_xlsx, listaTrabalhadores)


values_xlsx: pd.DataFrame  = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
valoresTemp_dict: dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']
valores_dict: dict = importar_Valores_Excel(valoresTemp_dict)
"""Dicionário com os valores do Excel, consumos, lucros..."""


competencias_xlsx: pd.DataFrame  = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
competencias_dict: dict  = competencias_xlsx.set_index('Skill').to_dict()['TimeActivity']
"""Dicionário com todas as competências do Excel"""


'''
    heat map por hora de marcação, mais escuro, mais tarde a hora de marcação
'''
plot_heatmap_activities_by_hour(listaAtividades)


listaBlocoTrabalho: list[BlocoTrabalho] = preencherListaWorkBlocks(listaTrabalhadores)
"""Lista com todos os blocos de trabalho"""

processarOpcao(considerarAgendamento, considerarPrioridade, metodoCluster, gmaps, dicionario_distancias, listaAtividades, listaTrabalhadores, valores_dict, competencias_dict, listaBlocoTrabalho)

'''
    Análises estatísticas
'''

plot_activities_graph_by_state(listaAtividades)

data = AnalisaDadosPorHora(listaAtividades)
sorted_stats_list = sorted(data)
print('Atividades por hora agendamento (0 é sem agendamento):')
for dat in sorted_stats_list:
    dat.print()

data = AnalisaDadosPorSkill(listaAtividades)
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
print("Quantidade Node:", No.quantidadeNos)

end_time = datetime.now() # type: ignore
elapsed_time = (end_time - start_time).total_seconds()
print("Tempo decorrido:", elapsed_time, "segundos")
