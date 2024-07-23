from datetime import datetime, time

from Workers import Worker, WorkBlock, Find_Worker_By_Id
from Helper import Distance_Calculator, activitiesToState1
from Activity import Activity
from Stats import WorkBlockStats
from Ploting import plot_activities_by_order, plot_scatter_with_trendline
from Optimization import Greedy


def DBSCANComplementar(list_activities: list [Activity], list_workers: list[Worker], work_Block: WorkBlock, cluster: list [Activity], distance_Min: int, distance_Max: int, iterations_Max: int) -> list[Activity]:
    """DBSCAN que começa a partir do KNN, recebe uma lista de atividades, um cluster, a começa a expandi lo

    Args:
        list_activities (list[Activity]): lista com todas as atividades
        list_workers (list[Worker]): lista com todos os trabalhadores
        work_Block (WorkBlock): lista com todos os blocos de trabalho
        cluster (list[Activity]): cluster inicial para ser expandido
        distance_Min (int): distancia minima para o DBSCAN adaptavel
        distance_Max (int): distancia máxima para o DBSCAN adaptavel
        iterations_Max (int): quantidade de iterações

    Returns:
        list[Activity]: cluster final
    """

    # encontrar o worker
    worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

    # executar a quantidade definida de iterações
    for i in range(iterations_Max):

        # cumprimento inicial do raio
        radius = distance_Min

        # tamanho anterior do cluster, para verificar se conseguiram ser adicionadas atividades
        previous_size = len(cluster)

        # lista vazia para as atividades antes de serem adicionadas ao cluster final
        temp_cluster = []

        # fica no loop enquanto não forem adicionadas novas atividades, ou então não chegar ao limite máximo do cumprimento do raio
        while previous_size == len(cluster) and radius <= distance_Max:

            # percorre as atividades do cluster
            for activity_clustered in cluster:

                # percorre todas as atividades
                for activity in list_activities:

                    # verifica que o estado é igual a 0
                    if activity.state == 0:

                        # calcula a distancia entre a atividade do cluster e a atividade da lista de todas as atividades
                        distance = Distance_Calculator(activity.latitude, activity.longitude, activity_clustered.latitude, activity_clustered.longitude)

                        # verifica se está dentro do raio
                        if distance < radius:
                            
                            # Verifica se a atividade está dentro do bloco de trabalho
                            agendamento_dentro_do_bloco = (
                                activity.agendamento < work_Block.fim and 
                                activity.agendamento > work_Block.inicio
                            )

                            # Verifica se a atividade não tem agendamento
                            agendamento_a_meia_noite = activity.agendamento == time(0, 0)

                            # Verifica se a competência da atividade está nas competências do trabalhador
                            competencia_adequada = activity.competencia in worker.competencia

                            # Combina todas as condições
                            if (agendamento_dentro_do_bloco or agendamento_a_meia_noite) and competencia_adequada:
                                temp_cluster.append(activity)
                                activity.state = 2

            if len( temp_cluster) == 0:
                radius += 1
            else:
                cluster.extend(temp_cluster)

    return cluster



def DBSCANInicio(list_activities: list[Activity], list_workers: list[Worker], work_Block: WorkBlock, distance_Min: int, distance_Max: int, iterations_Max: int) -> list[Activity]:
    """A partir do ponto de partida do trabalhador começa a adicionar atividades a um cluster, de acordo com o algoritmo DBSCAN

    Args:
        list_activities (list[Activity]): lista de todas as atividades
        list_workers (list[Worker]): lista de todos os trabalhadores
        work_Block (WorkBlock): lista de todos os workblocks
        distance_Min (int): distancia minima para o DBSCAN variavel
        distance_Max (int): distancia maxima para o DBSCAN variavel
        iterations_Max (int): quantidade de iteraçoes do DBSCAN

    Returns:
        list[Activity]: lista de atividades do cluster criado
    """

    def adicionar_atividades_ao_cluster(atividades: list[Activity], referencia_lat: float, referencia_long: float):
        """Adiciona atividades ao cluster temporário com base na distância e condições.

        Args:
            atividades (list[Activity]): lista com todas as atividades
            referencia_lat (float): latitude a comparar
            referencia_long (float): longitude a comparar
        """
        for activity in atividades:
            if activity.state == 0:
                distance = Distance_Calculator(activity.latitude, activity.longitude, referencia_lat, referencia_long)
                if distance <= radius:
                    agendamento_dentro_do_bloco = (activity.agendamento < work_Block.fim and activity.agendamento > work_Block.inicio)
                    agendamento_a_meia_noite = (activity.agendamento == time(0, 0))
                    competencia_adequada = (activity.competencia in worker.competencia)
                    if (agendamento_dentro_do_bloco or agendamento_a_meia_noite) and competencia_adequada:
                        temp_cluster.append(activity)
                        activity.state = 2


    # encontrar o trabalhador a que pertence o bloco de trabalho
    worker: Worker = Find_Worker_By_Id(list_workers, work_Block.idWorker)

    # cluster vazio
    cluster: list[Activity] = []
    
    # igual o raio ao cumprimento minimo
    radius: int = distance_Min

    # lista temporária para colocar as atividades antes de as adicionar ao cluster
    temp_cluster: list[Activity]  = []
   
    for i in range(iterations_Max):
        # Loop enquanto não forem adicionadas novas atividades ou o raio não atingir o limite máximo
        while len(temp_cluster) == 0 and radius <= distance_Max:

            # Adiciona atividades baseadas na posição do trabalhador
            adicionar_atividades_ao_cluster(list_activities, work_Block.latitude, work_Block.longitude)
            
            # Adiciona atividades baseadas nas atividades já no cluster
            for atividade_Cluster in cluster:
                adicionar_atividades_ao_cluster(list_activities, atividade_Cluster.latitude, atividade_Cluster.longitude)
            
            radius += 1

        # Adiciona atividades temporárias ao cluster principal e limpa a lista temporária
        cluster.extend(temp_cluster)
        if len(cluster) > 10:
            break

        # todo #2 colocar limite na quantidade de atividade
        temp_cluster.clear()

    return cluster






def Opcao_DBSCAN(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], dicionario_distancias: dict, competencias_dict: dict, valores_dict: dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    """Faz a ateribuição de atividades pelo DBSCAN

    Args:
        listaAtividades (list[Activity]): lista de todas as atividades
        listaTrabalhadores (list[Worker]): lista de todos os trabalhadores
        listaBlocoTrabalho (list[WorkBlock]): lista de todos os blocos trabalho
        dicionario_distancias (dict): dicionário com os tempos de viagem já calculadas
        competencias_dict (dict): dicionário com as competencias, e o tempo de realização das atividades
        valores_dict (dict): dicionário com os valores de configuração
        considerarAgendamento (bool): bool com a opção de considerar tipo agendamento
        considerarPrioridade (bool): bool com a opção de considerar prioridade
        gmaps (_type_): _description_
    """

    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), '\nMIN_DBSCAN_DISTANCE:', valores_dict['MIN_DBSCAN_DISTANCE'], 'MAX_DBSCAN_DISTANCE:', valores_dict['MAX_DBSCAN_DISTANCE'], 'DBSCANS_IT_NUM:', int(valores_dict['DBSCAN_IT_NUM']))

    for blocoTrabalho in listaBlocoTrabalho:
        
        # trabalhador do bloco de trabalho a ser atribuido
        trabalhador: Worker = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        
        # competencias do trabalhador
        competencias: list[str] = trabalhador.competencia
        
        # vai criar o clustar para o bloco de trabalho
        cluster = DBSCANInicio(listaAtividades, listaTrabalhadores, blocoTrabalho, valores_dict['MIN_DBSCAN_DISTANCE'], valores_dict['MAX_DBSCAN_DISTANCE'], int(valores_dict['DBSCAN_IT_NUM']))

        # chama o metodo de atribuição
        nodes = Greedy(cluster, listaTrabalhadores, blocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        
        # altera o estado das atividades para 1 (atribuidas)
        activitiesToState1(nodes, listaAtividades)

        # colocar todas as atividades que não têm o state igual a 1 a 0
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()

    return