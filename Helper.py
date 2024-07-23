from datetime import datetime
import math

from Activity import Activity, Find_Activity_By_Id
from Node import Node
from Workers import Worker, WorkBlock

def activitiesToState1(nodes: list [Node], list_activities: list[Activity]):
    """Altera o estado de todas as atividades atribuidas para 1

    Args:
        nodes (list[Node]): lista de nós com ids das atividades que foram atribuidas
        list_activities (list[Activity]): lista de todas as atividades
    """
    for node in nodes:
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            activity.state = 1


# devolve a quantidade de Minutos necessários para relizar o trajeto
def Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps):
    Travel_Time.quantidade_de_chamadas += 1
    return int(Distance_Calculator( lat1, lon1, lat2, lon2) * travel_mult) # values_dict['TRAVEL_TIME']

Travel_Time.quantidade_de_chamadas = 0

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


def Quantidade_Chamadas():
    return Travel_Time.quantidade_de_chamadas


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

def importarAtividadesExcel(activities_xlsx, listaAtividades):
    for indice, element in activities_xlsx.iterrows():
        if element['ComprirAgendamento'] == 0:
            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date()))
        # listaAtividades.append(Activity(element['NUMINT'], element['Central'], element['CodigoPostal'], element['Skill'], element['Latitude'], element['Longitude']))
        else:
            listaAtividades.append(Activity(id = element['NUMINT'], Central = element['Central'], competencia = element['Skill'], longitude = element['Longitude'], latitude = element['Latitude'], data_criacao = datetime.strptime(element['DataCriacao'], '%d/%m/%y').date(), agendamento = datetime.strptime(element['HoraAgendamento'], '%H:%M').time()))


def importarTrabalhadoresExcel(workers_xlsx, listaTrabalhadores):
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


def importarValoresExcel(valoresTemp_dict):
    precoCombustivelLitro = valoresTemp_dict['Preço_Combustível']
    custoTrabalhadorHora = valoresTemp_dict['Custo_Trabalhador']
    velocidadeMediaViagemKMpH = valoresTemp_dict['Média_Velocidade_Viagem']
    comsumoMedioCombustivel100km = valoresTemp_dict['Consumo_Combustível']
    valorRecebimentoHora = valoresTemp_dict['Recebimento']

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

    valores_dict = {}

    valores_dict['tempoViagem1KM'] = velocidadeMediaViagemMpKM
    valores_dict['multViagemReal'] = comsumoMedioCombustivelEmEuro1m
    valores_dict['multCustoTrabalhador'] = valorCustoTrabalhadorMin
    valores_dict['multRecebimentoTrabalho'] = valorRecebimentoMin
    
    return valores_dict

def preencherListaWorkBlocks(listaTrabalhadores):
    '''
    Fazer uma lista só com os workblocks para se irem adicionamdo as atividades a estes
'''

    listaBlocoTrabalho = []
    for worker in listaTrabalhadores:
        for workBlock in worker.work_Blocks:
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

