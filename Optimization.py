from ast import List
import heapq
from bson import _get_decimal128
import pandas as pd

from Activity import Atividade, Encontrar_Atividade_Por_Id
from Node import No
from Workers import BlocoTrabalho, Trabalhador, Find_Worker_By_Id
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

    # calcular o custo do trabalhador mais o custo da viagem
    custo = ((tempo_entre_atividades + tempo_em_atividade) * multTrabalhador) + (tempo_em_viagem * multViagemReal)

    # calcular o lucro obtido com a realização da atividade
    lucro = tempo_em_atividade * values_dict['multRecebimentoTrabalho']

    # verificar se é para daar prioridade as atividades de cumprir agendamento
    if considerAppointment and agendamento:

        # multiplicar o lucro pelo valor definido
        lucro = lucro * values_dict['PRIORITY_APPOINTMENT']


    # verificar se é para daar prioridade as atividades de acordo com a data de criação
    lucro = considerarPrioridadeCriação(dataCriacao, values_dict, considerPriority, lucro)

    # devolve a diferença entre o custo e o lucro
    return (lucro - custo)

def considerarPrioridadeCriação(dataCriacao, values_dict, considerPriority, lucro):
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
    return lucro


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

    # calcular o custo do trabalhador mais o custo da viagem
    cost = (((tempo_entre_atividades + tempo_em_viagem) * multTrabalhador) + (tempo_em_viagem * multViagemReal))

    # da return ao custo, mas negativo porque é uma despesa
    return (-cost)


def adicionar_Minutos_A_DatetimeTime(tim: time, min: int) -> time:
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


def Greedy(cluster_Atividades: list[Atividade], list_workers: list[Trabalhador], workBlock: BlocoTrabalho, dicionario_distancias: dict, competencias_dict: dict, values_dict: dict, considerAppointment: bool, considerPriority: bool, gmaps) -> list[No]:
    """verifica qual a melhor combinação de atividades para o trabalhador, faz lhe a rota e devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades

    Args:
        cluster_Atividades (list[Atividade]): lista com todas as atividades
        list_workers (list[Trabalhador]): lista com todos os trabalhadores
        workBlock (BlocoTrabalho): bloco de trabalho a ser atribuido
        dicionario_distancias (dict): dicionário com as distancias já calculadas
        competencias_dict (dict): dicionário com as competências e o tempo de realização das atividades
        values_dict (dict): dicionário com valores importados do Excel
        considerAppointment (bool): True se for para considerar a prioridade de tipo de agendamento, False se não
        considerPriority (bool): True se for para considerar a prioridade de data de criação, False se não
        gmaps (_type_): _description_

    Returns:
        list[No]: lista de nós pela ordem a serem percorridas
    """

    # este import teve de vir para aqui para evitar as importações circulares
    from Helper import pedir_Travel_Time, DateTimeTimeParaMinutosDoDia
    
    fronteira: list[No] = [] # lista com todos os nos da fronteira



    '''
    Importar uns valores e guardar em vars para usar depois
    '''
    tempoViagem1KM: float = values_dict['tempoViagem1KM']
    tolerancia_Atividade_Post: int = int (values_dict['WINDOW_TIME_POST'])
    tolerancia__Atividade_Pre: int = int (values_dict['WINDOW_TIME_PRE'])

    # inicio é o WorkBlock
    fronteira.append(No(workBlock.idTrabalhador, 0, 0,workBlock.inicio, workBlock.inicio, None))

    # enquanto existirem elementos na lista fronteira, ou então quando um ramo finalizado ele termina
    while fronteira:

        # ordena a fronteira por lucro, mais lucro, primeiro
        fronteira = sorted(fronteira)

        # escolhe o no com o melhor custo
        no_Atual = fronteira[0]

        # retira o no da fronteira
        fronteira.remove(no_Atual)

        # verifica o estado do no
        if(no_Atual.estado == 0):
            '''aqui ele entra se já tiver chegado ao fim, a ultima atividade'''

            caminho_Em_Nos = Caminho_Nos(no_Atual)

            # retirar o primeiro e ultimo no para o colocar no bloco de trabalho (o primeiro e o ultimo são casa)
            workBlock.atribuir_Nos_Bloco_Trabalho(caminho_Em_Nos[1:-1])

            # dar return a lista
            return caminho_Em_Nos
        
        tempo_Atual, atividade_Atual, encontrou_Atividade = local_Atual(cluster_Atividades, list_workers, no_Atual)


        # aqui percorre todas as atividades do cluster, isto para as tentar adicionar a rota
        for atividade in cluster_Atividades:
            
            
            tempoEmMinParaIrParaAAtividade, tempoEmMinParaVoltarACasa, horaDeChegadaAAtividade = calcular_Tempos(workBlock, dicionario_distancias, gmaps, tempoViagem1KM, tempo_Atual, atividade_Atual, atividade)

            # Tempo em minutos necessárioa para realizar a Atividade em si
            tempoNecessarioParaRealizarAtividade = competencias_dict[atividade.competencia]


            # verificar se a atividade já foi usada antes neste ramo, basicamente anda para trás a ver as tarefas anteriores, se não estiver lá ele deixa, se estivar lá, não deixa
            if not atividade.idAtividade in no_Atual.family :

                # as atividades com o tempo de agendamento == 00:00 não têm de cumprir o agendamento, ou seja podem ser realizadas a qualquer hora.

                
                ''' 
                Para entrar aqui:
                     - tem de cumprir o agendamento
                '''
                if not atividade.agendamento == time(0, 0):

                    # aqui adiciona o tolerance_For_Atividade_Post retirado do Excel, que é o tempo que pode chegar atrasado, 
                    max_Time_Atividade: time = adicionar_Minutos_A_DatetimeTime(atividade.agendamento, tolerancia_Atividade_Post)
                    """tempo máximo para chegar a atividade"""
                
                    
                    ''' 
                    Para entrar aqui:
                         - tem de cumprir o agendamento
                         - consegue chegar antes do limite máximo de atraso
                    Ou seja:
                         - dependendo do seguinte, pode ser atribuida a a tividade
                    '''
                    if horaDeChegadaAAtividade <= max_Time_Atividade:

                        # aqui adiciona o tolerance_For_Atividade_Post retirado do Excel, que é o tempo que pode chegar atrasado, 
                        horaMinimaParaAdiantamento = subtrairMinutosADatetimeTime(atividade.agendamento, tolerancia__Atividade_Pre)

                        ''' 
                        Para entrar aqui:
                             - tem de cumprir o agendamento
                             - consegue chegar antes do limite máximo de atraso
                             - consegue chegar depois do limite máximo de adiantamento
                        Ou seja:
                             - assim que chegar pode começar a trabalhar imediatamente
                        '''
                        if horaDeChegadaAAtividade >= horaMinimaParaAdiantamento:
                            
                            # Hora a que acaba a Tarefa
                            atividade_End_Time_Real =  adicionar_Minutos_A_DatetimeTime(horaDeChegadaAAtividade, tempoNecessarioParaRealizarAtividade)

                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            atividade_End_Time_Home = adicionar_Minutos_A_DatetimeTime(atividade_End_Time_Real, tempoEmMinParaVoltarACasa)

                            '''
                            Para entrar aqui:
                                 - tem de cumprir o agendamento
                                 - consegue chegar a atividade antes do limite máximo de atraso
                                 - consegue chegar a atividade depois do limite máximo de adiantamento
                                 - consegue chegar a casa depois do limite máximo de adiantamento
                            Ou seja:
                                 - pode ser adicionada a atividade pois tem tempo de a realizar e voltar a casa a tempo
                            '''
                            if atividade_End_Time_Home < workBlock.fim:
                                
                                # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                                encontrou_Atividade = True

                                # Minuto do dia em que Começa a Atividade
                                MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaDeChegadaAAtividade)

                                # Minuto do dia em que Acaba a Atividade Anterior
                                MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(tempo_Atual)

                                # Calcular o Custo de Realização desta Atividade
                                cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade,tempoNecessarioParaRealizarAtividade, True, atividade.data_criacao, values_dict, considerAppointment, considerPriority)
                                
                                # Adicionar nova Atividade a lista da Fronteira 
                                fronteira.append(No(atividade.idAtividade, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, atividade_End_Time_Real, no_Atual))


                            '''
                        Para entrar aqui:
                             - tem de cumprir o agendamento
                             - consegue chegar antes a atividade do limite máximo de atraso
                             - NÃO consegue chegar a atividade depois do limite máximo de adiantamento, tem de esperar
                        Ou seja:
                             - quando chegar tem de ficar a espera da hora de adiantamento
                        '''
                        else:
                            
                            # Tempo em que acaba a Tarefa
                            atividade_End_Time_Real = adicionar_Minutos_A_DatetimeTime(horaMinimaParaAdiantamento, tempoNecessarioParaRealizarAtividade)

                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            atividade_End_Time_Home = adicionar_Minutos_A_DatetimeTime(atividade_End_Time_Real, tempoEmMinParaVoltarACasa)

                            '''
                            Para entrar aqui:
                                 - tem de cumprir o agendamento
                                 - consegue chegar a atividade antes do limite máximo de atraso
                                 - NÃO consegue chegar a atividade depois do limite máximo de adiantamento
                                 - consegue chegar a casa depois do limite máximo de adiantamento
                            Ou seja:
                                 - pode ser adicionada a atividade pois tem tempo de a realizar e voltar a casa a tempo, mas antes de começar a atividade tem de ficar a espera
                            '''
                            if atividade_End_Time_Home < workBlock.fim:
                                # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                                encontrou_Atividade = True
                                
                                # Minuto do dia em que Começa a Atividade
                                MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaMinimaParaAdiantamento)

                                # Minuto do dia em que Acaba a Atividade Anterior
                                MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(tempo_Atual
                    )

                                # Calcular o Custo de Realização desta Atividade
                                cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade, tempoNecessarioParaRealizarAtividade, True, atividade.data_criacao, values_dict, considerAppointment, considerPriority)
                                
                                # Adicionar nova Atividade a lista da Fronteira
                                fronteira.append(No(atividade.idAtividade, cost, tempoEmMinParaIrParaAAtividade, horaMinimaParaAdiantamento, atividade_End_Time_Real , no_Atual))


                    ''' 
                Para entrar aqui:
                     - não tem de cumprir o agendamento
                '''
                else:
                    # Tempo em que acaba a Tarefa
                    atividade_End_Time_Real = adicionar_Minutos_A_DatetimeTime( horaDeChegadaAAtividade, tempoNecessarioParaRealizarAtividade)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    atividade_End_Time_Home = adicionar_Minutos_A_DatetimeTime( atividade_End_Time_Real, tempoEmMinParaVoltarACasa)

                    if atividade_End_Time_Home < workBlock.fim:
                        # Encontrou uma atividade entao passa isso a true para não entrar no if lá em baixo
                        encontrou_Atividade = True

                        # Minuto do dia em que Começa a Atividade
                        MinutosDoDiaComecarAtividade = DateTimeTimeParaMinutosDoDia(horaDeChegadaAAtividade)

                        # Minuto do dia em que Acaba a Atividade Anterior
                        MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(tempo_Atual
            )
                        
                        # Calcular o Custo de Realização desta Atividade
                        cost = CostCalculator(MinutosDoDiaComecarAtividade - MinutosDoDiaAcabarAtividadeAnterior, tempoEmMinParaIrParaAAtividade, tempoNecessarioParaRealizarAtividade, False, atividade.data_criacao, values_dict, considerAppointment, considerPriority)

                        # Adicionar nova Atividade a lista da Fronteira
                        fronteira.append(No(atividade.idAtividade, cost, tempoEmMinParaIrParaAAtividade, horaDeChegadaAAtividade, atividade_End_Time_Real , no_Atual))

        ''' 
        Para entrar aqui:
             - percorreu todas as atividades e não encontrou nenhuma que se encaixasse neste ramo
        '''
        if not encontrou_Atividade:
            
            # Minuto do dia em que Acaba a Atividade
            minutesDayStart = DateTimeTimeParaMinutosDoDia(tempo_Atual
)

            # Minuto do dia em que Acaba o dia
            minutesDayEnd = DateTimeTimeParaMinutosDoDia(workBlock.fim)

            tempoEmMinParaVoltarACasa: int = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade_Atual.latitude, atividade_Atual.longitude, workBlock.latitude, workBlock.longitude, gmaps) 

            # Calcular o Custo de volta a casa
            cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, tempoEmMinParaVoltarACasa, values_dict)

            noVolta: No = No(workBlock.idTrabalhador, cost, tempoEmMinParaVoltarACasa, workBlock.fim, workBlock.fim, no_Atual)
            noVolta.estado = False
            fronteira.append(noVolta)
           
      
    '''
        Acabaou a Fronteira, supostamente não aconteceria, mas vai que né
    '''
    path = []
    while no_Atual:
        path.append(no_Atual)
        no_Atual = no_Atual.pai
    return path[::-1]

def calcular_Tempos(workBlock: BlocoTrabalho, dicionario_distancias: dict, gmaps, tempoViagem1KM: float, tempo_Atual: time, atividade_Atual: Atividade | Trabalhador, atividade: Atividade) -> tuple[int,int,time]:
    """Calcula o tempo em minutos para chegar a atividade, o tempo em minutos para voltar a casa e a hora de chegada a casa

    Args:
        workBlock (BlocoTrabalho): bloco de trabalho que está a ser atribuido
        dicionario_distancias (dict): dicionário com as distâncias já calculadas
        gmaps (_type_): _description_
        tempoViagem1KM (float): tempo de viagem para percorrer 1km
        tempo_Atual (time): tempo atual da atribuição
        atividade_Atual (Atividade | Trabalhador): última realizada
        atividade (Atividade): atividade de ser considerada

    Returns:
        tuple[int,int,time]: [quantidade de minutos para chegar a atividade, tempo em minutos para voltar a casa, hora de chegada a casa]
    """


    from Helper import pedir_Travel_Time

    # Tempo necessário para se deslocar até a Atividade
    tempoEmMinParaIrParaAAtividade = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade_Atual.latitude, atividade_Atual.longitude, atividade.latitude, atividade.longitude, gmaps) 

    # Tempo necessário para se deslocar da Atividade até Casa
    tempoEmMinParaVoltarACasa = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade.latitude, atividade.longitude, workBlock.latitude, workBlock.longitude, gmaps)

    # Hora de Chegada a Atividade
    horaDeChegadaAAtividade = adicionar_Minutos_A_DatetimeTime(tempo_Atual, tempoEmMinParaIrParaAAtividade)

    return tempoEmMinParaIrParaAAtividade,tempoEmMinParaVoltarACasa,horaDeChegadaAAtividade










def local_Atual(worker_Activities_Cluster: list[Atividade], list_workers: list[Trabalhador], no_Atual: No)-> tuple[time, Atividade | Trabalhador, bool]:

    # a hora em que o node atual acabou, a hora a partir da qual vamos começar
    tempo_Atual = no_Atual.tempo_Fim

    # se encontrar atividade passa a true, se não conseguir encontrar mais atividades, volta para casa
    encontrou_Atividade = False

        # aqui temos um problema pois se no futuro se for possivel um trabalhador e uma atividade terem o mesmo id, isto começa a dar raia

    # como só guardamos o id da atividade no nó, vamos buscar a última atividade realizada pelo id
    atividade_Atual = Encontrar_Atividade_Por_Id(worker_Activities_Cluster,no_Atual.id)

    # se não existir uma atividade com o id é porque é um trabalhador
    if not atividade_Atual:
        atividade_Atual = Find_Worker_By_Id(list_workers, no_Atual.id)
    
    return tempo_Atual, atividade_Atual, encontrou_Atividade
















def Caminho_Nos(ultimo_No: No) -> list[No]:
    """Pega no Nó atual, segue a hierarquia a cima a até voltar ao inicio, inverte o caminho, e devolve

    Args:
        no_Atual (No): nó atual

    Returns:
        list[No]: lista de nós a percorrer
    """
    
    # cria a lista para colocar os nos por ordem
    path = []

    # preenche a lista ao contrário (da folha até a raiz) 
    while ultimo_No:
        path.append(ultimo_No)
        ultimo_No = ultimo_No.pai
            
    # inverter a lista
    path_invertido = path[::-1]
    return path_invertido
