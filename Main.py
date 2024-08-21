# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:43:14 2024

@author: jgac0
"""
import pandas as pd

from tkinter import N
import googlemaps
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd

from Activity import Atividade

from Helper import importar_Atividades_Excel, importar_Trabalhadores_Excel, importar_Valores_Excel, preencherListaWorkBlocks, CalcularQuantidadeAtividadesRealizadas

from Printer import processarOpcao

from Workers import Trabalhador

from Node import No

def main(metodoCluster: int, dbscan_min: int, dbscan_max: int , dbscan_ite: int, knn_ite: int, tempo_dep: int, tempo_ant: int) -> list:


    gmaps = ''
    No.quantidadeNos = 0
    # dicuinário coma s distâncias já calculadas
    dicionario_distancias = {}

    # ler dados do Excel
    activities_xlsx = pd.read_excel('DATA.xlsx', sheet_name='ACTIVITIES')
    listaAtividades: list[Atividade] = []
    importar_Atividades_Excel(activities_xlsx, listaAtividades)


    workers_xlsx = pd.read_excel('DATA.xlsx', sheet_name='WORKERS') # type: ignore
    listaTrabalhadores: list[Trabalhador] = []
    importar_Trabalhadores_Excel(workers_xlsx, listaTrabalhadores)


    values_xlsx = pd.read_excel('DATA.xlsx', sheet_name='VALUES')
    valoresTemp_dict = values_xlsx.set_index('VARIABLE').to_dict()['VALUE']
    valores_dict = importar_Valores_Excel(valoresTemp_dict)
    
    valores_dict['MIN_DBSCAN_DISTANCE'] = dbscan_min
    valores_dict['MAX_DBSCAN_DISTANCE'] = dbscan_max
    valores_dict['DBSCAN_IT_NUM']       = dbscan_ite
    valores_dict['K_NEAREST_NEIGHBORS'] = knn_ite

    valores_dict['WINDOW_TIME_POST']    = tempo_dep
    valores_dict['WINDOW_TIME_PRE']     = tempo_ant

    competencias_xlsx = pd.read_excel('DATA.xlsx', sheet_name='SKILLS')
    competencias_dict = competencias_xlsx.set_index('Skill').to_dict()['TimeActivity']


    listaBlocoTrabalho = preencherListaWorkBlocks(listaTrabalhadores)


    processarOpcao(False, False, metodoCluster, gmaps, dicionario_distancias, listaAtividades, listaTrabalhadores, valores_dict, competencias_dict, listaBlocoTrabalho)

    quantidadeAtividade = CalcularQuantidadeAtividadesRealizadas(listaAtividades)
    quantidadeAtividadePercent = float(quantidadeAtividade) / 10

    return [ quantidadeAtividadePercent, len(dicionario_distancias), No.quantidadeNos]
