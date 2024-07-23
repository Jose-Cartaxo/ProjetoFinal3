from KNearest_Neighbors import Opcao_K_NearestNeighbors_Adaptado, Opcao_K_NearestNeighbors_Normal, Opcao_K_N_DBSCAN
from DBSCAN import Opcao_DBSCAN
from Central import Opcao_Agrupamento_Por_Central
       

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
