from Activity import Atividade
from KNearest_Neighbors import Opcao_K_NearestNeighbors_Adaptado, Opcao_K_NearestNeighbors_Normal, Opcao_K_N_DBSCAN
from DBSCAN import Opcao_DBSCAN
from Central import Opcao_Agrupamento_Por_Central
from Workers import BlocoTrabalho, Trabalhador
       

def printCadaOpcao() -> None:
    """Faz o print de cada opção para clustering
    """
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


def solicitar_input(min: int, max: int) -> int:
    """Pede um input entre o min e max fornecido, devolve esse valor

    Args:
        min (int): Valor mínimo de input
        max (int): Valor máximo de outut

    Returns:
        int: Valor de input introduzido
    """

    while True:
        try:
            valor = int(input('Por favor, insira um número entre ' + str(min) + ' e ' + str(max) +': '))
            if min <= valor <= max:
                return valor
            else:
                print("Valor fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")


def pedir_s_n() -> bool:
    """Pergunta sim ou não, com respetiva resposta s, n
    se Sim devolve True, se Não devolve False

    Returns:
        bool: True ou False
    """

    while True:
        inp = input('"s" para sim, "n" para não: ')
        if inp != 's' and inp != 'n':
            print('Input errado! Tente novamente.')
        else:
            if inp == 'n':
                return False
            return True

def processarOpcao(considerarAgendamento: bool, considerarPrioridade: bool, metodoCluster: int, gmaps, dicionario_distancias: dict, listaAtividades: list[Atividade], listaTrabalhadores: list[Trabalhador], valores_dict: dict, competencias_dict: dict, listaBlocoTrabalho: list[BlocoTrabalho]) -> None:
    """Verifica qual o método de clustering escolhido e chama as funções de acordo

    Args:
        considerarAgendamento (bool): bool para a consideração de prioridade de acordo com o tipo de agendamento
        considerarPrioridade (bool): bool para a consideração de prioridade de acordo com a data de criação
        metodoCluster (int): método de clustering escolhido
        gmaps (_type_): _description_
        dicionario_distancias (dict): dicionário com as distâncias já calculadas
        listaAtividades (list[Atividade]): lista com todas as atividades 
        listaTrabalhadores (list[Trabalhador]): lista com todos os trabalhadores
        valores_dict (dict): dicionário com valores
        competencias_dict (dict): dicionário com as competências
        listaBlocoTrabalho (list[WorkBlock]): lista com todos os blocos de trabalho
    """

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
