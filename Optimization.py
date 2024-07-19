from ast import List
import heapq

from bson import _get_decimal128
from Activity import Activity, Find_Activity_By_Id
from Node import Node
from Workers import WorkBlock, Worker
from Workers import Find_Worker_By_Id
from DBSCAN import pedir_Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def CostCalculator(tempo_entre_atividades, tempo_em_viagem, tempo_em_atividade, agendamento, dataCriacao, values_dict, considerAppointment, considerPriority):
    """
    Esta função calcula o custo, tem em conta se o utilizador pretende dar prioridade às atividade mais antigas ou às atividades com agendamento a cumprir ou não.

    Parameters
    ----------
    tempo_entre_atividades: (int)
        quantidade de tempo em minutos gasta.
    tempo_em_viagem: (float)
        quantidade de tempo em minutos gasta em viagem.
    agendamento: (bool)
        se tem agendamento ou não.
    dataCriacao: (datetime.date)
        data de criação da atividade pode ser usadao caso o utilizador queira dar prioridade as atividades agendadas a mais tempo
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
    considerAppointment: (bool)
        bool que se for true significa que o utilizador quer considerar as atividades com agendamento mais prioritárias do que as sem, false são todas iguais
    considerPriority: (bool)
        bool que se for true significa que o utilizador quer considerar as atividades com agendamento mais antigo mais prioritárias do que as com mais recente, false são todas iguais

        
    Returns
    -------
    int
        Retorna o custo da viagem até a atividade.
    """

    multViagemReal = values_dict['multViagemReal']
    labor_Price_Min = values_dict['multCustoTrabalhador']

    custo = ((tempo_entre_atividades + tempo_em_atividade) * labor_Price_Min) + (tempo_em_viagem * multViagemReal)

    lucro = tempo_em_atividade * values_dict['multRecebimentoTrabalho']

    if considerAppointment and agendamento:
        lucro = lucro * values_dict['PRIORITY_APPOINTMENT']
    if considerPriority:
        dataHoje = datetime.now().date()
        diferencadias = (dataHoje - dataCriacao).days
        diferencaSemanas = diferencadias // 7
        mult = values_dict['PRIORITY_CREATION'] ** diferencaSemanas
        lucro = lucro * mult

    return (lucro - custo)


def CostCalculatorBackHome(tempo_entre_atividades, travel_time, values_dict):
    """
    Esta função calcula o custo de viagem de volta a casa.

    Parameters
    ----------
    tempo_entre_atividades: (int)
        quantidade de tempo em minutos gasta.
    travel_time: (float)
        quantidade de tempo em minutos gasta em viagem.
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        
    Returns
    -------
    Int
        Retorna o custo da viagem de volta a casa.
    """

    multViagemReal = values_dict['multViagemReal']
    labor_Price_Min = values_dict['multCustoTrabalhador']

    cost = (((tempo_entre_atividades + travel_time) * labor_Price_Min) + (travel_time * multViagemReal))

    return (0 - cost)


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


def adicionarMinutosADatetimeTime(tim, min):
    """
    Esta função faz a conta, adicionando à hora fornecida os minutos fornecidos, e devolve o resultado

    Parameters
    ----------
    tim: (datetime.time)
        hora sujeita a subração.
    min: (Int)
        quantidade de minutos a adicionar.
        
    Returns
    -------
    datetime.time
        devolve a hora após a conta
    """

    minutosTotais = tim.minute + min

    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = minutosTotais // 60
    minutos = minutosTotais % 60

    horas = tim.hour + quantidadeDeHoras 
    horas = horas
    if horas > 23:
        return time(23,59)

    return time(horas, minutos)


def subtrairMinutosADatetimeTime(tim, min):
    """
    Esta função faz a conta, subtraindo a hora fornecida os minutos fornecidos, e devolve o resultado

    Parameters
    ----------
    tim: (datetime.time)
        hora sujeita a subração.
    min: (Int)
        quantidade de minutos a subtrair.
        
    Returns
    -------
    datetime.time
        devolve a hora após a conta
    """

    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = min // 60
    min = min % 60
    
    horas = tim.hour - quantidadeDeHoras
    
    if min > tim.minute:
        horas = horas - 1
        min = 60 - (min - tim.minute)
    else: 
        min = tim.minute - min 

    horas = horas % 24
    if horas < 0:
        horas = horas + 24
    
    saida = time(horas, min)
    return saida


def Greedy(worker_Activities_Cluster: list[Activity], workBlock: WorkBlock, dicionario_distancias, competencias_dict, list_workers, values_dict, considerAppointment, considerPriority, gmaps):

    """
    Esta função verifica qual a melhor combinação de atividades para o trabalhador, faz lhe a rota e devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades.

    Parameters
    ----------
    worker_Activities_Cluster: (list of Activity.Activity)
        quantidade de tempo em minutos gasta.
    workBlock: (Workers.WorkBlock)
        quantidade de tempo em minutos gasta em viagem.
    competencias_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    list_workers: (list of Workers.Worker)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    considerAppointment: (bool)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    considerPriority: (bool)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    gmaps: (googlemaps.client.Client)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        
    Returns
    -------
    list of Node
        devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades
    """

    # Aqui cria uma lista "frontier", para guardar os nós que estão na fronteira
    frontier: list[Node] = []
    

    # atribuição das vars constantes que vêm do dicionário, que veio do Excel
    travel_Time_By_1KM = values_dict['tempoViagem1KM']
    tolerance_For_Activity_Post = int (values_dict['WINDOW_TIME_POST'])
    tolerance_For_Activity_Pre = int (values_dict['WINDOW_TIME_PRE'])

    # inicio é o WorkBlock
    frontier.append(Node(workBlock.idWorker, 0, 0,workBlock.inicio, workBlock.inicio, None))

    # enquanto existirem elementos na lista "frontier", ou então quando um ramo finalizado voltar a ser escolhido ele dá o ghost

    while frontier:

        frontier = sorted(frontier)


        current_Node = frontier[0]
        # print('Escolhido:', current_Node.id, 'Custo:', current_Node.total_cost) 
        # print('')
        # print('')
        frontier.remove(current_Node)
        if(current_Node.state == 0):
            # AQUI VAI DEVOLVER A MELHOR SOLUÇÃO DESCOBERTA
            # trabalhador = Find_Worker_By_Id(list_workers, workBlock.idWorker)
            path = []
            while current_Node:
                path.append(current_Node)
                current_Node = current_Node.parent
            
            # inverter a lista
            path_invertido = path[::-1]
            workBlock.atribuirNodeWorkBlock(path_invertido[1:-1])
            return path_invertido
        
        # a hora em que o node atual acabou, a hora a partir da qual vamos começar
        current_Time = current_Node.end_Time

        # se encontrar atividade passa a true, isto para ser usado mais a frente, pois se não conseguir encontrar mais atividades, volta para casa
        foundActivity = False

        # aqui temos um problema pois se no futuro se for possivel um trabalhador e uma atividade terem o mesmo id, isto começa a dar raia
        # como só guardamos o id da tarefa no nó, vamos buscar a última atividade realizada pelo id
        current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

        # se não existir uma atividade com o id é por que é porque é um trabalhador, por exemplo o primeiro nó da lista
        if not current_Activity:
            current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)


        # aqui percorre todas as atividades do cluster, isto para as tentar adicionar a rota
        for activity in worker_Activities_Cluster:
            
            
            # Tempo necessário para se deslocar até a Atividade
            tempoEmMinParaIrParaAAtividade = pedir_Travel_Time(dicionario_distancias, travel_Time_By_1KM, current_Activity.latitude, current_Activity.longitude, activity.latitude, activity.longitude, gmaps) # type: ignore

            # Tempo necessário para se deslocar da Atividade até Casa
            tempoEmMinParaVoltarACasa = pedir_Travel_Time(dicionario_distancias, travel_Time_By_1KM, activity.latitude, activity.longitude, workBlock.latitude, workBlock.longitude, gmaps)

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
                    max_Time_Activity = adicionarMinutosADatetimeTime(activity.agendamento, tolerance_For_Activity_Post)
                
                    
                    ''' 
                    Para entrar aqui:
                         - tem de cumprir o agendamento
                         - consegue chegar antes do limite máximo de atraso
                    Ou seja:
                         - dependendo do seguinte, pode ser atribuida a a tividade
                    '''
                    if horaDeChegadaAAtividade <= max_Time_Activity:

                        # aqui adiciona o tolerance_For_Activity_Post retirado do Excel, que é o tempo que pode chegar atrasado, 
                        horaMinimaParaAdiantamento = subtrairMinutosADatetimeTime(activity.agendamento, tolerance_For_Activity_Pre)
                        
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
                                frontier.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, activity_End_Time_Real, current_Node))


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
                                frontier.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaMinimaParaAdiantamento, activity_End_Time_Real , current_Node))


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
                        frontier.append(Node(activity.idActivity, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, activity_End_Time_Real , current_Node))

        ''' 
        Para entrar aqui:
             - percorreu todas as atividades e não encontrou nenhuma que se encaixasse neste ramo
        '''
        if not foundActivity:
            
            # Minuto do dia em que Acaba a Atividade
            minutesDayStart = DateTimeTimeParaMinutosDoDia(current_Time)

            # Minuto do dia em que Acaba o dia
            minutesDayEnd = DateTimeTimeParaMinutosDoDia(workBlock.fim)

            tempoEmMinParaVoltarACasa = pedir_Travel_Time(dicionario_distancias, travel_Time_By_1KM, current_Activity.latitude, current_Activity.longitude, workBlock.latitude, workBlock.longitude, gmaps) # type: ignore

            # Calcular o Custo de volta a casa
            cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, tempoEmMinParaVoltarACasa, values_dict)

            noVolta: Node = Node(workBlock.idWorker, cost, tempoEmMinParaVoltarACasa, workBlock.fim, workBlock.fim, current_Node)
            noVolta.state = 0
            frontier.append(noVolta)


            

           
      
    '''
        Acabaou a Fronteira, supostamente não aconteceria, mas vai que né
    '''
    path = []
    while current_Node:
        path.append(current_Node)
        current_Node = current_Node.parent
    return path[::-1]
