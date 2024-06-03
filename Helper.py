from traitlets import Float
from Activity import *
import math

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
        

def activitiesToState1(nodes, list_activities):
    for node in nodes:
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            activity.state = 1



# devolve a quantidade de Minutos necessários para relizar o trajeto
def Travel_Time( travel_mult, lat1, lon1, lat2, lon2, gmaps):
    return int(Distance_Calculator( lat1, lon1, lat2, lon2) * travel_mult) # values_dict['TRAVEL_TIME']

'''
def Travel_Time( travel_mult, x1, y1, x2, y2, gmaps):
    origem = (x1, y1)  # San Francisco, CA
    destino = (x2, y2)  # Los Angeles, CA
    result = gmaps.distance_matrix(origem, destino, mode="driving")
    minutes = result['rows'][0]['elements'][0]['duration']['value'] / 60
    # print('De: ', origem, ' para: ',destino, ' demora: ', minutes, 'minutos.')
    return minutes
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
