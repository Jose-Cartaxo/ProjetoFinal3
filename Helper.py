from datetime import datetime
import math
import pandas as pd

from Activity import Atividade, Encontrar_Atividade_Por_Id
from Node import No
from Workers import Trabalhador, BlocoTrabalho

import os
import shutil



def CalcularQuantidadeAtividadesRealizadas(listaAtividades: list[Atividade]):
    total : int = 0
    for atividade in listaAtividades:
        if atividade.estado == 1:
            total += 1
    return total

def limpar_pasta(caminho_pasta):
    # Iterar por todos os arquivos e subpastas na pasta especificada
    for filename in os.listdir(caminho_pasta):
        file_path = os.path.join(caminho_pasta, filename)
        
        # Verifica se é um arquivo e remove
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
        # Verifica se é uma pasta e remove
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def actividades_Para_Estado_1(nodes: list [No], list_activities: list[Atividade]):
    """Altera o estado de todas as atividades atribuidas para 1

    Args:
        nodes (list[No]): lista de nós com ids das atividades que foram atribuidas
        list_activities (list[Activity]): lista de todas as atividades
    """
    for node in nodes:
        activity = Encontrar_Atividade_Por_Id(list_activities, node.id)
        if activity:
            activity.estado = 1


# devolve a quantidade de Minutos necessários para relizar o trajeto
def Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps):
    return int(Distance_Calculator( lat1, lon1, lat2, lon2) * travel_mult) # values_dict['TRAVEL_TIME']


def pedir_Travel_Time(dicionarioTempoViagem: dict, travel_mult: float, lat1: float, lon1: float, lat2: float, lon2: float, gmaps) -> int:
    """calcula a quantidade de tempo de viagem em minutos entre duas coordenadas

    Args:
        dicionario (dict): dicionário com os tempos de viagem já calculador
        travel_mult (float): multiplicador do tempo de viagem
        lat1 (float): latitude ponto 1
        lon1 (float): longitude ponto 1
        lat2 (float): latitude ponto 2
        lon2 (float): longitude ponto 2
        gmaps (_type_): _description_

    Returns:
        int: tempo em minutos de viagem
    """
    
    chave = str(lat1 + lon1 + lat2 + lon2)

    if chave not in dicionarioTempoViagem:
        valor = Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps)
        dicionarioTempoViagem[chave] = valor
        return valor
    else:
        return dicionarioTempoViagem[chave]


'''
def Travel_Time( travel_mult, x1, y1, x2, y2, gmaps):
    origem = (x1, y1)  # San Francisco, CA
    destino = (x2, y2)  # Los Angeles, CA
    result = gmaps.distance_matrix(origem, destino, mode="driving")
    minutes = result['rows'][0]['elements'][0]['duration']['value'] / 60
    # print('De: ', origem, ' para: ',destino, ' demora: ', minutes, 'minutos.')
    return int(minutes)
'''



# devolve a distancia em KM entre 2 pontos
def Distance_Calculator( lat1, lon1, lat2, lon2) -> float:
    R = 6373.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def importar_Atividades_Excel(activities_xlsx: pd.DataFrame, listaAtividades: list [Atividade]):
    """Importa os dados das atividades do Excel para a lista fornecida

    Args:
        activities_xlsx (_type_): _description_
        listaAtividades (list[Activity]): _description_
    """
    for indice, element in activities_xlsx.iterrows():
        if element['ComprirAgendamento'] == 0:
            listaAtividades.append(Atividade(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
        # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
        else:
            listaAtividades.append(Atividade(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(), agendamento = datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))


def importar_Trabalhadores_Excel(workers_xlsx, listaTrabalhadores):
    for indice, element in workers_xlsx.iterrows():
        hours_str = element['HorarioTrabalho']
        hours_list = hours_str.split(',')
        tempo_listaBlocoTrabalho = []
        i = 0
        for hours in hours_list:
            start_hour, end_hour = hours.split(';')
            tempo_listaBlocoTrabalho.append(BlocoTrabalho(element['idTrabalhador'], element['Longitude'], element['Latitude'], i,start_hour, end_hour))
            i += 1
    
        listaTrabalhadores.append(Trabalhador(element['idTrabalhador'], element['Central'], [item.strip() for item in  element['Skills'].split(',')]  , element['Longitude'], element['Latitude'], tempo_listaBlocoTrabalho))


def importar_Valores_Excel(valoresTemp_dict: dict) -> dict:
    """Recebe um dicionário com valores do Excel, transforma os para ser aplicaveis. Ex transforma 7 litros de consumo por 100km e uma velocidade média de 60 km/h, em consumo médio por minuto de viagem.

    Args:
        valoresTemp_dict (dict): dicionário com valores do Excel

    Returns:
        dict: dicionário com valores aplicaveis
    """

    precoCombustivelLitro = valoresTemp_dict['Preço_Combustível']
    custoTrabalhadorHora = valoresTemp_dict['Custo_Trabalhador']
    velocidadeMediaViagemKMpH = valoresTemp_dict['Média_Velocidade_Viagem']
    comsumoMedioCombustivel100km = valoresTemp_dict['Consumo_Combustível']
    valorRecebimentoHora = valoresTemp_dict['Recebimento']
    valorPenalizacaoOciosoHora = valoresTemp_dict['Penalizacao_Ocioso']

#  Calcular quantos Km faz num minutos
    velocidadeMediaViagemKMpM = velocidadeMediaViagemKMpH / 60;
# Calcular quantos minutos demora a fazer um Km
    velocidadeMediaViagemMpKM = 1 / velocidadeMediaViagemKMpM;

# Quanto Combustivel gasta a fazer 1 Km
    comsumoMedioCombustivel1km = comsumoMedioCombustivel100km / 100;
# Quanto Combustivel em Litros gasta em 1 Min
    comsumoMedioCombustivelEmLitros1m = comsumoMedioCombustivel1km * velocidadeMediaViagemKMpM;

# Quanto Combustivel em Euros gasta em 1 Min
    comsumoMedioCombustivelEmEuro1m = comsumoMedioCombustivelEmLitros1m * precoCombustivelLitro;   

# Lucro por Min de trabalho do trabalhadar a realizar atividades
    valorCustoTrabalhadorMin = custoTrabalhadorHora / 60;

# Lucro por Min de trabalho do trabalhadar a realizar atividades
    valorRecebimentoMin = valorRecebimentoHora / 60;

# Penalizacao por Min de trabalho do trabalhadar a fazer nada
    valorPenalizacaoOciosoMin = valorPenalizacaoOciosoHora / 60;

    valores_dict = {}

    valores_dict['tempoViagem1KM'] = velocidadeMediaViagemMpKM
    valores_dict['multViagemReal'] = comsumoMedioCombustivelEmEuro1m
    valores_dict['multCustoTrabalhador'] = valorCustoTrabalhadorMin
    valores_dict['multRecebimentoTrabalho'] = valorRecebimentoMin
    valores_dict['multTempoOcioso'] = valorPenalizacaoOciosoMin
    valores_dict['WINDOW_TIME_POST'] = valoresTemp_dict['WINDOW_TIME_POST']
    valores_dict['WINDOW_TIME_PRE'] = valoresTemp_dict['WINDOW_TIME_PRE']
    valores_dict['MIN_DBSCAN_DISTANCE'] = valoresTemp_dict['MIN_DBSCAN_DISTANCE']
    valores_dict['MAX_DBSCAN_DISTANCE'] = valoresTemp_dict['MAX_DBSCAN_DISTANCE']
    valores_dict['DBSCAN_IT_NUM'] = valoresTemp_dict['DBSCAN_IT_NUM']
    valores_dict['K_NEAREST_NEIGHBORS'] = valoresTemp_dict['K_NEAREST_NEIGHBORS']
    valores_dict['PRIORITY_APPOINTMENT'] = valoresTemp_dict['PRIORITY_APPOINTMENT']
    valores_dict['PRIORITY_CREATION'] = valoresTemp_dict['PRIORITY_CREATION']
    valores_dict['RAIO_ANALISE'] = valoresTemp_dict['RAIO_ANALISE']

    return valores_dict

def preencherListaWorkBlocks(listaTrabalhadores: list[Trabalhador]) -> list[BlocoTrabalho]:
    """Coloca todos os blocos de trabalho de todos os trabalhadores em um lista.

    Args:
        listaTrabalhadores (list[Worker]): Lista com todos os trabalhadores

    Returns:
        list[BlocoTrabalho]: Lista com todos os blocos de trabalho
    """

    listaBlocoTrabalho = []
    for worker in listaTrabalhadores:
        for workBlock in worker.lista_Blocos_Trabalho:
            listaBlocoTrabalho.append(workBlock)
            
    return listaBlocoTrabalho


def DateTimeTimeParaMinutosDoDia(tim):
    """
    Esta função calcula o minuto do dia através do datetime.time fornecido.

    Parameters
    ----------
    tim: (datetime.time)
        datetime.time a ser convertido.
        
    Returns
    -------
    Int
        Retorna o minuto do dia calculado.
    """
    return (tim.hour * 60 + tim.minute)



def Encontrar_Atividade_or_Trabalhador_Por_Id(lista_atividades: list[Atividade], lista_trabalhadores: list[Trabalhador], id: str) -> Atividade | Trabalhador:
    
    for atividade in lista_atividades:
        if(atividade.idAtividade == id):
            return atividade
    
    for trabalhador in lista_trabalhadores:
        if(trabalhador.idTrabalhador == id):
            return trabalhador
    
    raise ValueError(f"ID {id} não encontrado na lista de atividades nem de trabalhadores")