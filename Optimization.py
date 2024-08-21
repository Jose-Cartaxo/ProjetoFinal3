from ast import List
import heapq
from bson import _get_decimal128
import pandas as pd

from Activity import Activity, Find_Activity_By_Id
from Node import Node
from Workers import WorkBlock, Worker, Find_Worker_By_Id
from datetime import datetime, time, date


def CostCalculator(tempo_entre_atividades: int, tempo_em_viagem: int, tempo_em_atividade: int, agendamento: bool, dataCriacao: date, values_dict: dict, considerAppointment: bool, considerPriority: bool) -> float:
    """calcula o custo, tem em conta se o utilizador pretende dar prioridade às atividade mais antigas ou às atividades com agendamento a cumprir ou não

    Args:
        tempo_entre_atividades (int): tempo entre as atividades, em minutos
        tempo_em_viagem (int): tempo em viagem entre as atividades, em minutos
        tempo_em_atividade (int): tempo em atividade
        agendamento (bool): se é do tipo de cumprir agendamento, True, se não, False
        dataCriacao (date): data da criação da atividade
        values_dict (dict): dicionário com valores importados do Excel para se utilizar nos cálculos
        considerAppointment (bool): se é para dar prioridade as atividade com cumprimento de agendamento
        considerPriority (bool): se é para dar prioridade as atividades com data de criação mais antiga

    Returns:
        float: valor do custo da realização desta atividade
    """

    # retirar o multiplicador do tempo de viagem do dicionário
    multViagemReal = values_dict['multViagemReal']

    # retirar o multiplicador do tempo de trabalho do dicionário
    multTrabalhador = values_dict['multCustoTrabalhador']

    # retirar o multiplicador do tempo ocioso do dicionário
    multOcioso = values_dict['multTempoOcioso']

    # calcular o custo do trabalhador mais o custo da viagem
    custo = ((tempo_entre_atividades + tempo_em_atividade) * multTrabalhador) + (tempo_em_viagem * multViagemReal)+ ((tempo_entre_atividades - tempo_em_viagem) * multOcioso)


    # calcular o lucro obtido com a realização da atividade
    lucro = tempo_em_atividade * values_dict['multRecebimentoTrabalho']

    # verificar se é para daar prioridade as atividades de cumprir agendamento
    if considerAppointment and agendamento:

        # multiplicar o lucro pelo valor definido
        lucro = lucro * values_dict['PRIORITY_APPOINTMENT']


    # verificar se é para daar prioridade as atividades de acordo com a data de criação
    if considerPriority:

        # verificar a data de hoje
        dataHoje = datetime.now().date()

        # diferenca de dias entre o dia de hoje e a data de criação da atividade
        diferencadias = (dataHoje - dataCriacao).days

        # transformar a diferença em dias, para diferença em semanas
        diferencaSemanas = diferencadias // 7

        # aumentar o multiplicador de forma proporcianal a quantidade de semanas
        mult = values_dict['PRIORITY_CREATION'] ** diferencaSemanas

        # multiplicar o lucro pelo valor definido
        lucro = lucro * mult

    # devolve a diferença entre o custo e o lucro
    return (lucro - custo)


def CostCalculatorBackHome(tempo_entre_atividades: int, tempo_em_viagem: int, values_dict: dict) -> float:
    """Calcula o custo de retornar a casa

    Args:
        tempo_entre_atividades (int): tempo entre as atividades, em minutos
        tempo_em_viagem (int): tempo em viagem ate casa, em minutos
        values_dict (dict): dicionário com valores importados do Excel para se utilizar nos cálculos

    Returns:
        float: valor do custo de volta a casa
    """

    # retirar o multiplicador do tempo de viagem do dicionário
    multViagemReal = values_dict['multViagemReal']

    # retirar o multiplicador do tempo de trabalho do dicionário
    multTrabalhador = values_dict['multCustoTrabalhador']

    # retirar o multiplicador do tempo ocioso do dicionário
    multOcioso = values_dict['multTempoOcioso']
    
    # calcular o custo do trabalhador mais o custo da viagem
    cost = (((tempo_entre_atividades + tempo_em_viagem) * multTrabalhador) + (tempo_em_viagem * multViagemReal))+ ((tempo_entre_atividades - tempo_em_viagem) * multOcioso)

    # da return ao custo, mas negativo porque é uma despesa
    return (-cost)


def adicionarMinutosADatetimeTime(tim: time, min: int) -> time:
    """adiciona uma quantidade de minutos a uma hora (hh:mm) do tipo datetime.time e devolve em datetime.time

    Args:
        tim (time): hora a ser acrescentado uma quantidade de minutos
        min (int): quantidade de minutos a adicionar

    Returns:
        time: hora com os minutos adicionados
    """

    # adiciona a quantidade de minutos da hora, com a quantidade de minutos a adicionar, faz a divisão inteira por 60 pois por cada 60 min completos, é uma hora que tem de se adicionar às horas, depois o resto desta divisão é a quantidade de minutos final
    minutosTotais = tim.minute + min

    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = minutosTotais // 60
    minutos = minutosTotais % 60

    horas = tim.hour + quantidadeDeHoras 
    horas = horas

    # como o algoritmo não funciona de um dia para o outro, caso tente ultrapassar para o próximo dia ele dá lhe a hora 23:59
    if horas > 23:
        return time(23,59)

    return time(horas, minutos)


def subtrairMinutosADatetimeTime(tim: time, min: int) -> time:
    """adiciona uma quantidade de minutos a uma hora (hh:mm) do tipo datetime.time e devolve em datetime.time

    Args:
        tim (time): hora a ser retirada uma quantidade de minutos
        min (int): quantidade de minutos a retirar

    Returns:
        time: hora com os minutos subtraidos
    """

    # divide a quantidade de horas da quantidade de minutos

    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = min // 60

    # quantidade de minutos restantes
    min = min % 60
    
    # subtrai a quantidade de horas
    horas = tim.hour - quantidadeDeHoras
    
    # se os minutos a subtrais forem menos do que tem, retira uma hora e depois retira a diferença do total
    if min > tim.minute:
        horas = horas - 1
        min = 60 - (min - tim.minute)
    else: 
        min = tim.minute - min 

    # como o algoritmo não funciona de um dia para o outro, caso tente ultrapassar para outro dia ele dá lhe a hora 00:01
    if horas < 0:
        return time(00,1)
    
    return time(horas, min)


def Greedy(worker_Activities_Cluster: list[Activity], list_workers: list[Worker], workBlock: WorkBlock, dicionario_distancias: dict, competencias_dict: dict, values_dict: dict, considerAppointment: bool, considerPriority: bool, gmaps) -> list[Node]:
    """verifica qual a melhor combinação de atividades para o trabalhador, faz lhe a rota e devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades

    Args:
        worker_Activities_Cluster (list[Activity]): lista com todas as atividades
        list_workers (list[Worker]): lista com todos os trabalhadores
        workBlock (WorkBlock): bloco de trabalho a ser atribuido
        dicionario_distancias (dict): dicionário com as distancias já calculadas
        competencias_dict (dict): dicionário com as competências e o tempo de realização das atividades
        values_dict (dict): dicionário com valores importados do Excel
        considerAppointment (bool): True se for para considerar a prioridade de tipo de agendamento, False se não
        considerPriority (bool): True se for para considerar a prioridade de data de criação, False se não
        gmaps (_type_): _description_

    Returns:
        list[Node]: lista de nós pela ordem a serem percorridas
    """

    # este import teve de vir para aqui para evitar as importações circulares
    from Helper import pedir_Travel_Time, DateTimeTimeParaMinutosDoDia
    
    # Aqui cria uma lista fronteira, para guardar os nós que estão na fronteira
    fronteira: list[Node] = []
    
    # atribuição das vars constantes que vêm do dicionário, que veio do Excel
    tempoViagem1KM = values_dict['tempoViagem1KM']
    tolerancia_Activity_Post = int (values_dict['WINDOW_TIME_POST'])
    tolerancia__Activity_Pre = int (values_dict['WINDOW_TIME_PRE'])

    # inicio é o WorkBlock
    fronteira.append(Node(workBlock.idWorker, 0, 0,workBlock.inicio, workBlock.inicio, None))

    # enquanto existirem elementos na lista fronteira, ou então quando um ramo finalizado ele termina
    while fronteira:

        # organiza a fronteira
        fronteira = sorted(fronteira)

        # escolhe o no com o melhor custo
        current_Node = fronteira[0]

        # retira o no da fronteira
        fronteira.remove(current_Node)

        # verifica o estado do no
        if(current_Node.state == 0):
            '''aqui ele entra se já tiver chegado ao fim, a ultima atividade'''

            # cria a lista para colocar os nos por ordem
            path = []

            # preenche a lista ao contrário (da folha até a raiz) 
            while current_Node:
                path.append(current_Node)
                current_Node = current_Node.parent
            
            # inverter a lista
            path_invertido = path[::-1]

            # retirar o primeiro e ultimo no para o colocar no bloco de trabalho (o primeiro e o ultimo são casa)
            workBlock.atribuirNodeWorkBlock(path_invertido[1:-1])

            # dar return a lista
            return path_invertido
        
        # a hora em que o node atual acabou, a hora a partir da qual vamos começar
        current_Time = current_Node.end_Time

        # se encontrar atividade passa a true, se não conseguir encontrar mais atividades, volta para casa
        foundActivity = False

        # aqui temos um problema pois se no futuro se for possivel um trabalhador e uma atividade terem o mesmo id, isto começa a dar raia
        # como só guardamos o id da atividade no nó, vamos buscar a última atividade realizada pelo id
        current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

        # se não existir uma atividade com o id é porque é um trabalhador
        if not current_Activity:
            current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)


        # aqui percorre todas as atividades do cluster, isto para as tentar adicionar a rota
        for activity in worker_Activities_Cluster:
            
            
            # Tempo necessário para se deslocar até a Atividade
            tempoEmMinParaIrParaAAtividade = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, current_Activity.latitude, current_Activity.longitude, activity.latitude, activity.longitude, gmaps) 

            # Tempo necessário para se deslocar da Atividade até Casa
            tempoEmMinParaVoltarACasa = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, activity.latitude, activity.longitude, workBlock.latitude, workBlock.longitude, gmaps)

            # Hora de Chegada a Atividade
            horaDeChegadaAAtividade = adicionarMinutosADatetimeTime(current_Time, tempoEmMinParaIrParaAAtividade)

            # verificar se a atividade já foi usada antes neste ramo, basicamente anda para trás a ver as tarefas anteriores, se não estiver lá ele deixa, se estivar lá, não deixa
            if not activity.idActivity in current_Node.family :

                # as atividades com o tempo de agendamento == 00:00 não têm de cumprir o agendamento, ou seja podem ser realizadas a qualquer hora.

                
                ''' 
                Para entrar aqui:
                     - tem de cumprir o agendamento
                '''
                if not activity.agendamento == time(0, 0):

                    # aqui adiciona o tolerance_For_Activity_Post retirado do Excel, que é o tempo que pode chegar atrasado, 
                    max_Time_Activity = adicionarMinutosADatetimeTime(activity.agendamento, tolerancia_Activity_Post)
                
                    
                    ''' 
                    Para entrar aqui:
                         - tem de cumprir o agendamento
                         - consegue chegar antes do limite máximo de atraso
                    Ou seja:
                         - dependendo do seguinte, pode ser atribuida a a tividade
                    '''
                    if horaDeChegadaAAtividade <= max_Time_Activity:

                        # aqui adiciona o tolerance_For_Activity_Post retirado do Excel, que é o tempo que pode chegar atrasado, 
                        horaMinimaParaAdiantamento = subtrairMinutosADatetimeTime(activity.agendamento, tolerancia__Activity_Pre)
                        
                        ''' 
                        Para entrar aqui:
                             - tem de cumprir o agendamento
                             - consegue chegar antes do limite máximo de atraso
                             - consegue chegar depois do limite máximo de adiantamento
                        Ou seja:
                             - assim que chegar pode começar a trabalhar imediatamente
                        '''
                        if horaDeChegadaAAtividade >= horaMinimaParaAdiantamento:
                            
                            # Tempo em minutos necessárioa para realizar a Atividade em si
                            tempoNecessarioParaRealizarAtividade = competencias_dict[activity.competencia]
                            
                            # Hora a que acaba a Tarefa
                            activity_End_Time_Real =  adicionarMinutosADatetimeTime(horaDeChegadaAAtividade, tempoNecessarioParaRealizarAtividade)

                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            activity_End_Time_Home = adicionarMinutosADatetimeTime(activity_End_Time_Real, tempoEmMinParaVoltarACasa)

                            '''
                            Para entrar aqui:
                                 - tem de cumprir o agendamento
                                 - consegue chegar a atividade antes do limite máximo de atraso
                                 - consegue chegar a atividade depois do limite máximo de adiantamento
                                 - consegue chegar a casa depois do limite máximo de adiantamento
                            Ou seja:
                                 - pode ser adicionada a atividade pois tem tempo de a realizar e voltar a casa a tempo
                            '''
                            if activity_End_Time_Home < workBlock.fim:
                                # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                                foundActivity = True

                                # Minuto do dia em que Começa a Atividade
                                MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaDeChegadaAAtividade)

                                # Minuto do dia em que Acaba a Atividade Anterior
                                MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(current_Time)

                                # Calcular o Custo de Realização desta Atividade
                                cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade,tempoNecessarioParaRealizarAtividade, True, activity.data_criacao, values_dict, considerAppointment, considerPriority)
                                
                                # Adicionar nova Atividade a lista da Fronteira 
                                fronteira.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, activity_End_Time_Real, current_Node))


                            '''
                        Para entrar aqui:
                             - tem de cumprir o agendamento
                             - consegue chegar antes a atividade do limite máximo de atraso
                             - NÃO consegue chegar a atividade depois do limite máximo de adiantamento, tem de esperar
                        Ou seja:
                             - quando chegar tem de ficar a espera da hora de adiantamento
                        '''
                        else:
                            # Tempo necessário para a Atividade em si
                            tempoNecessarioParaRealizarAtividade = competencias_dict[activity.competencia]
                            
                            # Tempo em que acaba a Tarefa
                            activity_End_Time_Real = adicionarMinutosADatetimeTime(horaMinimaParaAdiantamento, tempoNecessarioParaRealizarAtividade)

                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            activity_End_Time_Home = adicionarMinutosADatetimeTime(activity_End_Time_Real, tempoEmMinParaVoltarACasa)

                            '''
                            Para entrar aqui:
                                 - tem de cumprir o agendamento
                                 - consegue chegar a atividade antes do limite máximo de atraso
                                 - NÃO consegue chegar a atividade depois do limite máximo de adiantamento
                                 - consegue chegar a casa depois do limite máximo de adiantamento
                            Ou seja:
                                 - pode ser adicionada a atividade pois tem tempo de a realizar e voltar a casa a tempo, mas antes de começar a atividade tem de ficar a espera
                            '''
                            if activity_End_Time_Home < workBlock.fim:
                                # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                                foundActivity = True
                                
                                # Minuto do dia em que Começa a Atividade
                                MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaMinimaParaAdiantamento)

                                # Minuto do dia em que Acaba a Atividade Anterior
                                MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(current_Time)

                                # Calcular o Custo de Realização desta Atividade
                                cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade, tempoNecessarioParaRealizarAtividade, True, activity.data_criacao, values_dict, considerAppointment, considerPriority)
                                
                                # Adicionar nova Atividade a lista da Fronteira
                                fronteira.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaMinimaParaAdiantamento, activity_End_Time_Real , current_Node))


                    ''' 
                Para entrar aqui:
                     - não tem de cumprir o agendamento
                '''
                else:
                    # Tempo necessário para a Atividade em si
                    tempoNecessarioParaRealizarAtividade = competencias_dict[activity.competencia]
                    # Tempo em que acaba a Tarefa
                    activity_End_Time_Real = adicionarMinutosADatetimeTime( horaDeChegadaAAtividade, tempoNecessarioParaRealizarAtividade)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    activity_End_Time_Home = adicionarMinutosADatetimeTime( activity_End_Time_Real, tempoEmMinParaVoltarACasa)

                    if activity_End_Time_Home < workBlock.fim:
                        # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                        foundActivity = True

                        # Minuto do dia em que Começa a Atividade
                        MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaDeChegadaAAtividade)

                        # Minuto do dia em que Acaba a Atividade Anterior
                        MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(current_Time)
                        
                        # Calcular o Custo de Realização desta Atividade
                        cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade, tempoNecessarioParaRealizarAtividade, False, activity.data_criacao, values_dict, considerAppointment, considerPriority)

                        # Adicionar nova Atividade a lista da Fronteira
                        fronteira.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, activity_End_Time_Real , current_Node))

        ''' 
        Para entrar aqui:
             - percorreu todas as atividades e não encontrou nenhuma que se encaixasse neste ramo
        '''
        if not foundActivity:
            
            # Minuto do dia em que Acaba a Atividade
            minutesDayStart = DateTimeTimeParaMinutosDoDia(current_Time)

            # Minuto do dia em que Acaba o dia
            minutesDayEnd = DateTimeTimeParaMinutosDoDia(workBlock.fim)

            tempoEmMinParaVoltarACasa: int = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, current_Activity.latitude, current_Activity.longitude, workBlock.latitude, workBlock.longitude, gmaps)

            # Calcular o Custo de volta a casa
            cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, tempoEmMinParaVoltarACasa, values_dict)

            noVolta: Node = Node(workBlock.idWorker, cost, tempoEmMinParaVoltarACasa, workBlock.fim, workBlock.fim, current_Node)
            noVolta.state = 0
            fronteira.append(noVolta)


            

           
      
    '''
        Acabaou a Fronteira, supostamente não aconteceria, mas vai que né
    '''
    path = []
    while current_Node:
        path.append(current_Node)
        current_Node = current_Node.parent
    return path[::-1]
