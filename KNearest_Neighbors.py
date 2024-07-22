# from Helper import *
from Workers import Worker, WorkBlock, Find_Worker_By_Id, Node
from Activity import Activity
from Ploting import plot_activities_by_order, plot_scatter_with_trendline
from Optimization import Greedy
from Helper import Distance_Calculator, activitiesToState1
from datetime import datetime, time
from Stats import WorkBlockStats
from DBSCAN import DBSCAN1

class KNearest_Nei:
    def __init__(self, atividade, distancia):
        """
        Inicializa a MinhaClasse com um atividade e a distancia ao trabalhador.

       
        Parameters
        ----------
        atividade: (Atividade)
            Atividade que esta a ser ponderada.
        distancia: (Double) 
            distancia em KM entre o local de partida do trabalhador e a atividade.
        """
        self.atividade = atividade
        self.distancia = distancia
    # se for menor tem de retornar true
    def __lt__(self, other):
        return self.distancia < other.distancia


class Coordenada:
    def __init__(self, longitude, latitude):
        """
        Inicializa a MinhaClasse com um x e um y, que são as coordenadas.

       
        Parameters
        ----------
        x: (Int)
            coordenada do x.
        y: (Int) 
            coordendada do y.
        """
        self.longitude = longitude
        self.latitude = latitude


def KNearest_Neighbors_Vote_in(atividade: Activity, workblock: WorkBlock, competencias)-> bool:
    """
    Esta função verifica se a tarefa deve ser contada para o clustering do workblick ou não, verifica o estado da atividade, verifica o hora de marcação e se possiu as skills necessárias

    Parameters
    ----------
    kNearest_Nei: (KNearest_Nei)
        elemento a comparar com o bloco de trabalho para ver se entra.
    workblock: (WorkBlock)
        workblock que estamos a fazer o clustering das atividades para.
    skills: (list of str)
        lista das skills que o trabalhador possuiu.

    Returns
    -------
    bool
        retorna True ou False, conforme se é para ser adicionada a lista ou não.
    """

    if atividade.agendamento != time(0, 0):
  
        if (atividade.state != 1) and (atividade.agendamento < workblock.fim) and (atividade.agendamento > workblock.inicio) and (atividade.competencia in competencias):
            return True
   
    elif (atividade.state != 1) and (atividade.competencia in competencias):
        return True

    return False



def KNearest_Neighbors_Normal(list_activities, competencias, workblock, k):
    """
    Esta função faz o K-NEAREST-NEIGHBORS para o workblock submetido e devolve uma lista com o atividades do cluster

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades existentes.
    list_workers: (list of Worker)
        lista de todos as trabalhadores existentes.
    workblock: (WorkBlock)
        workblock que estamos a fazer o clustering das atividades para.
    k: (Int)
        quantidade de atividades a colocar no Cluster.

    Returns
    -------
    list of Activity
        retorna uma lista das k atividades mais próximas do local de partida do trabalhador.
    """
        
    distances = []
    # worker = Find_Worker_By_Id(list_workers, workblock.idWorker)

    for activity in list_activities:
        distance = Distance_Calculator(activity.latitude, activity.longitude, workblock.latitude, workblock.longitude)
        distances.append(KNearest_Nei(activity, distance))
    
    distances = sorted(distances)
    
    list_temp = []
    count = 0
    indi = 0
    while count < k:
        if indi < len(distances):
            if KNearest_Neighbors_Vote_in(distances[indi].atividade, workblock, competencias):
                distances[indi].atividade.state = 2
                list_temp.append(distances[indi].atividade)
                count += 1
            indi += 1
        else:
            break
    
    return  list_temp



def KNearest_Neighbors_Adaptado(list_activities, list_workers, workblock, k):
    """
    Esta função faz o clustering das atividades para o workblock.

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades a ponderar para o clustering.
    list_workers: (list of Workers)
        lista de todos os trabalhadores a ponderar para o clustering.
    workblock: (Workblock)
        workblock a ponderar para o clustering.
    k: (Int)
        quantidade de Atividades a colocar no cluster.

    Returns
    -------
    list of Activity
        Retorna uma lista de atividades, que é o cluster final.
    """

    # lista com os Atividades com a respetiva distancia
    distances = []

    # lista com as coordenadas dos elementos que já pertencem ao cluster
    list_coordenada_temp = []

    # lista com os elementes que já pertencem
    list_cluster = []

    # trabalhador que vai realizar este workblock
    worker = Find_Worker_By_Id(list_workers, workblock.idWorker)

    list_coordenada_temp.append(Coordenada(worker.longitude, worker.latitude)) # type: ignore
    for count in range(k):

        # colocar as atividades por ordem
        for activity in list_activities:

            # verificar se a atividade ainda não está a ser considerada.
            if activity.state == 0:
                for coord in list_coordenada_temp:
                    distance = Distance_Calculator(activity.latitude, activity.longitude, coord.latitude, coord.longitude)
                    if KNearest_Neighbors_Vote_in(activity, workblock, worker.competencia): # type: ignore
                        distances.append(KNearest_Nei(activity, distance))
        
        distances = sorted(distances)
        if len(distances) != 0:
            atividade_in = distances[0].atividade
            atividade_in.state = 2 
            list_coordenada_temp.append(Coordenada(atividade_in.longitude, atividade_in.latitude)) # type: ignore
            list_cluster.append(atividade_in)
            distances.clear()
            
        else:
            return list_cluster
        
    return list_cluster


def Opcao_K_NearestNeighbors_Adaptado(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias, skills_dict, valores_dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))

    for blocoTrabalho in listaBlocoTrabalho:

        cluster = KNearest_Neighbors_Adaptado(listaAtividades, listaTrabalhadores, blocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']))

        nodes: list[Node] = Greedy(cluster, blocoTrabalho, dicionario_distancias, skills_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        '''
        colocar as atividades que foram atribuidas com o state == 1
        '''

        activitiesToState1(nodes, listaAtividades)

        '''
        fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock
        '''

        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        '''
        colocar todas as atividades que não têm o state igual a 1 a 0
        '''
        
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()

        '''
        fazer um gráfico com a evolução da atribuição das atividades
        '''
        activityQuantity = len(nodes) - 1
        # activityQuantity = len(nodes) - 2

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

def Opcao_K_NearestNeighbors_Normal(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        competencias = trabalhador.competencia

        cluster = KNearest_Neighbors_Normal(listaAtividades, competencias, blocoTrabalho, int(valores_dict['K_NEAREST_NEIGHBORS']))
        nodes = Greedy(cluster, blocoTrabalho, dicionario_distancias, competencias_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        '''
            colocar as atividades que foram atribuidas com o state == 1
        '''
        activitiesToState1(nodes, listaAtividades)

        '''
            fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock
        '''
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        '''
            colocar todas as atividades que não têm o state igual a 1 a 0
        '''
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()


        '''
            fazer um gráfico com a evolução da atribuição das atividades
        '''
        activityQuantity = len(nodes) - 1
        # activityQuantity = len(nodes) - 2

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



def Opcao_K_N_DBSCAN(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    
    meio_dia = datetime.strptime('11:00:00', '%H:%M:%S').time()
    list_worker_activityQuantity = []

    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']), 'MIN_DBSCAN_DISTANCE:', valores_dict['MIN_DBSCAN_DISTANCE'], 'MAX_DBSCAN_DISTANCE:', valores_dict['MAX_DBSCAN_DISTANCE'], 'DBSCANS_IT_NUM:', int(valores_dict['DBSCAN_IT_NUM']))

    for blocoTrabalho in listaBlocoTrabalho:
        trabalhador = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        competencias = trabalhador.competencia
        
        cluster = KNearest_Neighbors_Normal(listaAtividades, competencias, blocoTrabalho, 4)
        cluster = DBSCAN1(listaAtividades, listaTrabalhadores, blocoTrabalho, cluster, valores_dict['MIN_DBSCAN_DISTANCE'], valores_dict['MAX_DBSCAN_DISTANCE'], int(valores_dict['DBSCAN_IT_NUM']))

        nodes = Greedy(cluster, blocoTrabalho, dicionario_distancias, competencias_dict, listaTrabalhadores, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        '''

        colocar as atividades que foram atribuidas com o state == 1
        '''
        activitiesToState1(nodes, listaAtividades)

        '''

        fazer um gráfico de pontos, com as coordenadas das atividades do cluster, e mostrar o percurso do trabalhador neste workblock


        '''
        plot_activities_by_order(cluster, nodes, blocoTrabalho)

        '''

        colocar todas as atividades que não têm o state igual a 1 a 0
        '''
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()


        '''

        fazer um gráfico com a evolução da atribuição das atividades
        '''
        activityQuantity = len(nodes) - 1
        # activityQuantity = len(nodes) - 2

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