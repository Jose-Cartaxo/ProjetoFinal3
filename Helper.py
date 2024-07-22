from traitlets import Float
from Activity import *
import math
from Workers import *
from KNearest_Neighbors import Opcao_K_NearestNeighbors_Adaptado, Opcao_K_NearestNeighbors_Normal, Opcao_K_N_DBSCAN
from DBSCAN import Opcao_DBSCAN
from Central import Opcao_Agrupamento_Por_Central



def solicitar_input(min, max):
    while True:
        try:
            valor = int(input('Por favor, insira um número entre ' + str(min) + ' e ' + str(max) +': '))
            if min <= valor <= max:
                return valor
            else:
                print("Valor fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")


def pedir_s_n():
    while True:
        inp = input('"s" para sim, "n" para não: ')
        if inp != 's' and inp != 'n':
            print('Input errado! Tente novamente.')
        else:
            if inp == 'n':
                return False
            return True
       
def printCadaOpcao():
    # 1 - K-NearestNeighbors 1.0
    # 2 - K-NearestNeighbors 2.0
    # 3 - K-NearestNeighbors com DBSCANS
    # 4 - DBSCANS
    # 5 - Central

    print("Qual metodo de clustering deseja utilizar?")
    print("1 - K-Nearest Neighbors (a comparar apenas ao ponto de partida)")
    print("2 - K-Nearest Neighbors adapatado (a comparar a todos os elementos pertencentes ao cluster)")
    print("3 - K-NearestNeighbors com DBSCANS (primeiro k nearest neighbors, depois o DBSCANS)")
    print("4 - DBCANS (normal)")
    print("5 - Central") 

def activitiesToState1(nodes, list_activities):
    for node in nodes:
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            activity.state = 1


# devolve a quantidade de Minutos necessários para relizar o trajeto
def Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps):
    Travel_Time.quantidade_de_chamadas += 1
    return int(Distance_Calculator( lat1, lon1, lat2, lon2) * travel_mult) # values_dict['TRAVEL_TIME']

Travel_Time.quantidade_de_chamadas = 0

def pedir_Travel_Time(dicionario, travel_mult, lat1, lon1, lat2, lon2, gmaps):
    
    chave = ((lat1, lon1), (lat2, lon2))

    if chave not in dicionario:
        valor = Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps)
        dicionario[chave] = valor
        return dicionario[chave]
    else:
        return dicionario[chave]


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
    print('multViagemReal:', valores_dict['multViagemReal'])
    print('multCustoTrabalhador:', valores_dict['multCustoTrabalhador'])
    print('multRecebimentoTrabalho:', valores_dict['multRecebimentoTrabalho'])
    print('multTempoOcioso:', valores_dict['multTempoOcioso'])
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


def processarOpcao(considerarAgendamento, considerarPrioridade, metodoCluster, gmaps, dicionario_distancias, listaAtividades, listaTrabalhadores, valores_dict, competencias_dict, listaBlocoTrabalho):
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
