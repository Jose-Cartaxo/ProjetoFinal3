from lib2to3.main import diff_texts

from traitlets import Integer
from Workers import Worker, WorkBlock, Find_Worker_By_Id, Node
from Activity import Activity
from Ploting import plot_activities_by_order, plot_scatter_with_trendline
from Optimization import Greedy
from Helper import Distance_Calculator, activitiesToState1
from datetime import datetime, time
from Stats import WorkBlockStats
from DBSCAN import DBSCANComplementar


def KNearest_Neighbors_Vote_in(atividade: Activity, workblock: WorkBlock, competencias: list[str])-> bool:
    """ver se o elemento entra

    Args:
        atividade (Activity): atividade a entrar
        workblock (WorkBlock): bloco de trabalho onde vai entrar
        competencias (_type_): lista de competencia do trabalhador

    Returns:
        bool: True se entra, False se não
    """

    if atividade.agendamento != time(0, 0):
  
        if (atividade.state != 1) and (atividade.agendamento < workblock.fim) and (atividade.agendamento > workblock.inicio) and (atividade.competencia in competencias):
            return True
   
    elif (atividade.state != 1) and (atividade.competencia in competencias):
        return True

    return False



def KNearest_Neighbors_Normal(list_activities: list[Activity], competencias: list[str], workblock: WorkBlock, k: int) -> list[Activity]:
    """Esta função faz o K-NEAREST-NEIGHBORS para o workblock submetido e devolve uma lista com o atividades do cluster

    Args:
        list_activities (list[Activity]):  lista com todas as atividades
        competencias (list[str]):  lista com as competencias do trabalhador
        workblock (WorkBlock): bloco de trabalho a fazer o clustering
        k (int): tamanho do cluster a criar

    Returns:
        list[Activity]: retorna o cluster criado, uma lista das k atividades mais próximas do local de partida do trabalhador.
    """
        
    # lista vazia para começar a colocar as distancias
    distances: list[tuple[Activity, float]] = []

    # percorre todas as atividades da listas
    for activity in list_activities:

        # calcula a distancia de cada uma das atividades
        distance = Distance_Calculator(activity.latitude, activity.longitude, workblock.latitude, workblock.longitude)

        # adiciona a atividade a lista, e a sua respetiva distancia
        distances.append((activity, distance))
    
    # organiza a lista de ordem crescente de distancia
    distances.sort(key=lambda x: x[1])
    
    # inicializa o cluster, para adicionar as atividades e depois o retornar
    cluster: list[Activity] = []

    # contagem da quantidade de elementos adicionados
    count: int = 0

    # indice da iteração entre os elementos da lista com as
    indi: int = 0

    # while que repete enquanto não encontrar a quantidade de atividade desejadas
    while count < k:

        # verificar se ainda existe lista
        if indi < len(distances):

            # ver se a atividade entra no cluster
            if KNearest_Neighbors_Vote_in(distances[indi][0], workblock, competencias):
                
                # alterar o estado da atividade para 2 (am análise)
                distances[indi][0].state = 2

                # adicionar a atividade a lista
                cluster.append(distances[indi][0])

                # aumentar a contagem de atividades
                count += 1

            # aumentar o indice
            indi += 1

        # verificar se ainda existe lista
        else:
            # se acabar a lista, sair do loop
            break
    
    # retornar o cluster
    return cluster



def KNearest_Neighbors_Adaptado(list_activities: list[Activity], list_workers: list[Worker], workblock: WorkBlock, k: int) -> list[Activity]:
    """ Esta função faz o K-NEAREST-NEIGHBORS adaptado para o workblock submetido e devolve uma lista com o atividades do cluster

    Args:
        list_activities (list[Activity]): lista com todas as atividades
        competencias (list[Worker]): lista com todos os trabalhadores
        workblock (WorkBlock): bloco de trabalho a fazer o clustering
        k (int): tamanho do cluster a criar

    Returns:
        list[Activity]: retorna o cluster criado, uma lista das k atividades mais próximas do local de partida do trabalhador.
    """

    # lista com os Atividades com a respetiva distancia
    distances: list[tuple[Activity, float]] = []

    # lista com as coordenadas dos elementos que já pertencem ao cluster
    list_coordenada_temp: list[tuple[float, float]]  = []

    # lista com os elementes que já pertencem
    list_cluster = []

    # trabalhador que vai realizar este workblock
    worker = Find_Worker_By_Id(list_workers, workblock.idWorker)

    # lista de coordenadas 
    list_coordenada_temp.append((worker.latitude, worker.longitude))

    for count in range(k):
        '''Basicamente para cada iteração do K adiciona uma atividade, esta atividade é escolhida sendo a atividade com menor distancia ou ao ponto central, o ponto de partida do trabalhador, ou às outras atividades que já pertencem, sempre que adiciona uma atividade adiciona as coordenadas dessa atividades a lista de coordenandas para depois comparar a essa atividade na próxima iteração
        '''

        # colocar as atividades por ordem
        for activity in list_activities:

            # verificar state == 0, não atribuida
            if activity.state == 0:

                # percorre a lista com as coordenadas
                for coord in list_coordenada_temp:

                    # calcula a distancia entre todas as atividades com state 0 e todas as coordenadas da lista de coordendas
                    distance = Distance_Calculator(activity.latitude, activity.longitude, coord[0], coord[1])

                    # adiciona as possiveis atividades a lista de distancias
                    if KNearest_Neighbors_Vote_in(activity, workblock, worker.competencia): # type: ignore
                        distances.append((activity, distance))
        
        # organiza a lista de ordem crescente de distancia
        distances.sort(key=lambda x: x[1])

        # verifica se a lista  não está vazia
        if len(distances) != 0:

            # retira  aatividade mais proxima
            atividade_in = distances[0][0]

            # altera o state da atividade para 2, a ser analisada
            atividade_in.state = 2 
            
            # adiciona a coordenada da atividade que entrou a lista de coordenadas
            list_coordenada_temp.append((atividade_in.longitude, atividade_in.latitude)) # type: ignore
            
            # adiciona a atividade ao cluster
            list_cluster.append(atividade_in)

            # limpa a lista das distancias
            distances.clear()
            
        else:
            return list_cluster
        
    return list_cluster



def Opcao_K_NearestNeighbors_Adaptado(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias, skills_dict, valores_dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    
    # Aqui guarda a hora "11:00" para depois comparar os blocos de trabalho da parte da manha e da parte da tarde
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    
    # lista com a quantidade de atividades realizadas pelos trabalhadores, por ordem
    list_worker_activityQuantity = []

    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))

    # percorre todos os blocos de trabalho
    for blocoTrabalho in listaBlocoTrabalho:

        # faz o agrupamento das atividades
        cluster: list[Activity] = KNearest_Neighbors_Adaptado(listaAtividades, listaTrabalhadores, blocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']))

        # faz a atribuição das atividades
        nodes: list[Node] = Greedy(cluster, listaTrabalhadores, blocoTrabalho, dicionario_distancias, skills_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        # colocar as atividades que foram atribuidas com o state == 1
        activitiesToState1(nodes, listaAtividades)

        # fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock 
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        # colocar todas as atividades que não têm o state igual a 1 a 0 
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()

        
        # fazer um gráfico com a evolução da atribuição das atividades
        activityQuantity = len(nodes) - 2 # (o -2 é para retirar o bloco de sair de casa, e voltar a casa)
        if blocoTrabalho.inicio < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)
    
    print('\nManha \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'manha':
            print(stat.quantidade, end=", ")
    print('\n\nTarde \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'tarde':
            print(stat.quantidade, end=", ")
    print('\n')

    return



def Opcao_K_NearestNeighbors_Normal(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias: dict, competencias_dict: dict, valores_dict: dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    """Trata de chamar as funções para a atribuição de atividades com o método de clustering KNNN

    Args:
        listaAtividades (list[Activity]): lista com todas as atividades
        listaTrabalhadores (list[Worker]): lista com todos os trabalhadores
        listaBlocoTrabalho (list[WorkBlock]): lista com todos os blocos de trabalho
        dicionario_distancias (dict): dicionário com todas as distâncias calculadas
        competencias_dict (dict): dicionário com todas as competências
        valores_dict (dict): dicionário com todos os valores
        considerarAgendamento (bool): bool para a consideração de prioridade de acordo com o tipo de agendamento
        considerarPrioridade (bool): bool para a consideração de prioridade de acordo com a data de criação
        gmaps (_type_): _description_
    """

    meio_dia: time = datetime.strptime('11:00:00', '%H:%M:%S').time()
    """Aqui guarda a hora "11:00" para depois comparar os blocos de trabalho da parte da manha e da parte da tarde"""
    
    list_worker_activityQuantity: list[WorkBlockStats] = []
    """lista com a quantidade de atividades realizadas pelos trabalhadores, por ordem"""
    
    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))

    # percorre todos os blocos de trabalho
    for blocoTrabalho in listaBlocoTrabalho:

        # trabalhador do bloco de trabalho
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        
        # competencias do trabalhador do bloco de trabalho
        competencias = trabalhador.competencia

        # faz o agrupamento das atividades
        cluster = KNearest_Neighbors_Normal(listaAtividades, competencias, blocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']))
        
        # faz a atribuição das atividades
        nodes = Greedy(cluster, listaTrabalhadores, blocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        # altera o estado das atividades para 1 (atribuidas)
        activitiesToState1(nodes, listaAtividades)

        # fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        # colocar todas as atividades que não têm o state igual a 1 a 0
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()

        # fazer um gráfico com a evolução da atribuição das atividades
        activityQuantity = len(nodes) - 2 # (o -2 é para retirar o bloco de sair de casa, e voltar a casa)
        if blocoTrabalho.inicio < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)
    print('\nManha \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'manha':
            print(stat.quantidade, end=", ")
    print('\n\nTarde \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'tarde':
            print(stat.quantidade, end=", ")
    print('\n')
            
    return



def Opcao_K_N_DBSCAN(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias: dict, competencias_dict: dict, valores_dict: dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    """Trata de chamar as funções para fazer a atribuição de atividades com o método de clutering KNN, DBSCAN

    Args:
        listaAtividades (list[Activity]): lista com todas as atividades
        listaTrabalhadores (list[Worker]): lista com todos os trabalhadores
        listaBlocoTrabalho (list[WorkBlock]): lista com todos os blocos de trabalho
        dicionario_distancias (dict): dicionário com todas as distâncias já calculadas
        competencias_dict (dict): dicionário com todas as competências
        valores_dict (dict): dicionário com todos os valores
        considerarAgendamento (bool): bool para a consideração de prioridade de acordo com o tipo de agendamento
        considerarPrioridade (bool): bool apra a consideração de prioridade de acordo com a data de criação
        gmaps (_type_): _description_
    """
    
    # Aqui guarda a hora "11:00" para depois comparar os blocos de trabalho da parte da manha e da parte da tarde
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    
    # lista com a quantidade de atividades realizadas pelos trabalhadores, por ordem
    list_worker_activityQuantity = []

    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']), 'MIN_DBSCAN_DISTANCE:', valores_dict['MIN_DBSCAN_DISTANCE'], 'MAX_DBSCAN_DISTANCE:', valores_dict['MAX_DBSCAN_DISTANCE'], 'DBSCANS_IT_NUM:', int(valores_dict['DBSCAN_IT_NUM']))

    # percorre todos os blocos de trabalho
    for blocoTrabalho in listaBlocoTrabalho:

        # trabalhador do bloco de trabalho
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        
        # competencias do trabalhador do bloco de trabalho
        competencias = trabalhador.competencia
        
        # começa o agrupamento das atividades
        cluster = KNearest_Neighbors_Normal(listaAtividades, competencias, blocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']))
        
        # acaba o agrupamento das atividades
        cluster = DBSCANComplementar(listaAtividades, listaTrabalhadores, blocoTrabalho, cluster, valores_dict['MIN_DBSCAN_DISTANCE'], valores_dict['MAX_DBSCAN_DISTANCE'], int(valores_dict['DBSCAN_IT_NUM']))

        # faz a atribuição das atividades
        nodes = Greedy(cluster, listaTrabalhadores, blocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        # colocar as atividades que foram atribuidas com o state == 1 
        activitiesToState1(nodes, listaAtividades)

        # fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock 
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        # colocar todas as atividades que não têm o state igual a 1 a 0 
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()


        # fazer um gráfico com a evolução da atribuição das atividades 
        activityQuantity = len(nodes) - 2

        if blocoTrabalho.inicio < meio_dia:
            list_worker_activityQuantity.append(WorkBlockStats('manha',activityQuantity))
        else:
            list_worker_activityQuantity.append(WorkBlockStats('tarde',activityQuantity))


    
    plot_scatter_with_trendline(list_worker_activityQuantity)

    print('\nManha \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'manha':
            print(stat.quantidade, end=", ")
    print('\n\nTarde \n')
    for stat in list_worker_activityQuantity:
        if stat.tipo == 'tarde':
            print(stat.quantidade, end=", ")
    print('\n')

    return


