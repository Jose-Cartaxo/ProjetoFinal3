from ast import List
import heapq
from bson import _get_decimal128
import pandas as pd

from Activity import Atividade
from Node import No
from Workers import BlocoTrabalho, Trabalhador
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
    multOcioso = values_dict['Penalizacao_Ocioso']

    # calcular o custo do trabalhador mais o custo da viagem
    custo = ((tempo_entre_atividades + tempo_em_atividade) * multTrabalhador) + (tempo_em_viagem * multViagemReal) + ((tempo_entre_atividades - tempo_em_viagem) * multOcioso)

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


def Greedy(cluster_Atividades: list[Atividade], lista_Trabalhadores: list[Trabalhador], blocoTrabalho: BlocoTrabalho, dicionario_distancias: dict, competencias_dict: dict, values_dict: dict, considerar_Agendamento: bool, considerar_Data_Criacao: bool, gmaps) -> list[No]:
    """verifica qual a melhor combinação de atividades para o trabalhador, faz lhe a rota e devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades

    Args:
        cluster_Atividades (list[Atividade]): lista com todas as atividades
        lista_Trabalhadores (list[Trabalhador]): lista com todos os trabalhadores
        blocoTrabalho (BlocoTrabalho): bloco de trabalho a ser atribuido
        dicionario_distancias (dict): dicionário com as distancias já calculadas
        competencias_dict (dict): dicionário com as competências e o tempo de realização das atividades
        values_dict (dict): dicionário com valores importados do Excel
        considerar_Agendamento (bool): True se for para considerar a prioridade de tipo de agendamento, False se não
        considerar_Data_Criacao (bool): True se for para considerar a prioridade de data de criação, False se não
        gmaps (_type_): _description_

    Returns:
        list[No]: lista de nós pela ordem a serem percorridas
    """

    # este import teve de vir para aqui para evitar as importações circulares
    from Helper import pedir_Travel_Time, DateTimeTimeParaMinutosDoDia, Encontrar_Atividade_or_Trabalhador_Por_Id
    
    fronteira: list[No] = [] # lista com todos os nos da fronteira


    '''
    Importar uns valores e guardar em vars para usar depois
    '''
    tempoViagem1KM: float = values_dict['tempoViagem1KM']

    # inicio é o blocoTrabalho
    fronteira.append(No(blocoTrabalho.idTrabalhador, 0, 0,blocoTrabalho.inicio, blocoTrabalho.inicio, None))

    # enquanto existirem elementos na lista fronteira, ou então quando um ramo finalizado ele termina
    while fronteira:

        # ordena a fronteira por lucro, mais lucro, primeiro
        fronteira = sorted(fronteira)

        # escolhe o no com o melhor custo
        no_Atual = fronteira[0]

        # retira o no da fronteira
        fronteira.remove(no_Atual)

#--------------------------------
        if(no_Atual.estado == 0):
            """aqui ele entra se já tiver chegado ao fim, a ultima atividade"""

            caminho_Em_Nos = Caminho_Nos(no_Atual)

            # retirar o primeiro e ultimo no para o colocar no bloco de trabalho (o primeiro e o ultimo são casa)
            blocoTrabalho.atribuir_Nos_Bloco_Trabalho(caminho_Em_Nos[1:-1])

            # dar return a lista
            return caminho_Em_Nos
#--------------------------------
        

        atividade_Atual = Encontrar_Atividade_or_Trabalhador_Por_Id(cluster_Atividades, lista_Trabalhadores, no_Atual.id)

        encontrou_Atividade = False


        for atividade in cluster_Atividades:
            """Percorre todas as atividades do cluster, para as tentar adicionar a seguir a este nó"""
            
            tempo_De_Viagem_Para_A_Atividade = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade_Atual.latitude, atividade_Atual.longitude, atividade.latitude, atividade.longitude, gmaps) 
            
            tempo_De_Viagem_Para_Voltar_A_Casa = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade.latitude, atividade.longitude, blocoTrabalho.latitude, blocoTrabalho.longitude, gmaps)

            # Hora de Chegada a Atividade
            hora_De_Chegada_A_Atividade = adicionar_Minutos_A_DatetimeTime(no_Atual.tempo_Fim, tempo_De_Viagem_Para_A_Atividade)

            # Tempo em minutos necessárioa para realizar a Atividade em si
            tempo_Para_Realizar_Atividade = competencias_dict[atividade.competencia]

            if not atividade.idAtividade in no_Atual.familia:
                """Verifica se esta atividade já não pertence ao ramo deste nó"""

                if not atividade.agendamento == time(0, 0):
                    """ Tem de cumprir o agendamento, tem a janela de tempo para realizar a atividade
                    """
                    encontrou_Atividade = atribuir_Atividade_Com_Agendamento(blocoTrabalho, values_dict, considerar_Agendamento, considerar_Data_Criacao, fronteira, no_Atual, atividade, tempo_De_Viagem_Para_A_Atividade, tempo_De_Viagem_Para_Voltar_A_Casa, hora_De_Chegada_A_Atividade, tempo_Para_Realizar_Atividade)

                else:
                    """ Não tem de cumprir o agendamento, pode começar a realizar a atividade a qualquer hora
                    """

                    encontrou_Atividade = atribuir_Atividade_Sem_Agendamento(blocoTrabalho, values_dict, considerar_Agendamento, considerar_Data_Criacao, fronteira, no_Atual, atividade, tempo_De_Viagem_Para_A_Atividade, tempo_De_Viagem_Para_Voltar_A_Casa, hora_De_Chegada_A_Atividade, tempo_Para_Realizar_Atividade)

        ''' 
        Para entrar aqui:
             - percorreu todas as atividades e não encontrou nenhuma que se encaixasse neste ramo
        '''
        if not encontrou_Atividade:
            
            # Minuto do dia em que Acaba a Atividade
            minutesDayStart = DateTimeTimeParaMinutosDoDia(no_Atual.tempo_Fim)

            # Minuto do dia em que Acaba o dia
            minutesDayEnd = DateTimeTimeParaMinutosDoDia(blocoTrabalho.fim)

            tempoEmMinParaVoltarACasa: int = pedir_Travel_Time(dicionario_distancias, tempoViagem1KM, atividade_Atual.latitude, atividade_Atual.longitude, blocoTrabalho.latitude, blocoTrabalho.longitude, gmaps) 

            # Calcular o Custo de volta a casa
            cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, tempoEmMinParaVoltarACasa, values_dict)

            noVolta: No = No(blocoTrabalho.idTrabalhador, cost, tempoEmMinParaVoltarACasa, blocoTrabalho.fim, blocoTrabalho.fim, no_Atual)
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















def atribuir_Atividade_Sem_Agendamento(workBlock, values_dict, considerAppointment, considerPriority, fronteira, no_Atual, atividade, tempo_De_Viagem_Para_A_Atividade, tempo_De_Viagem_Para_Voltar_A_Casa, hora_De_Chegada_A_Atividade, tempo_Para_Realizar_Atividade):
    
    from Helper import DateTimeTimeParaMinutosDoDia
    
    atividade_Hora_Fim_Real = adicionar_Minutos_A_DatetimeTime( hora_De_Chegada_A_Atividade, tempo_Para_Realizar_Atividade)

    atividade_Hora_Chegar_Casa = adicionar_Minutos_A_DatetimeTime( atividade_Hora_Fim_Real, tempo_De_Viagem_Para_Voltar_A_Casa)

    if atividade_Hora_Chegar_Casa < workBlock.fim:

        minutos_Do_Dia_Comecar_Atividade = DateTimeTimeParaMinutosDoDia(hora_De_Chegada_A_Atividade)

        MinutosDoDiaAcabarAtividadeAnterior = DateTimeTimeParaMinutosDoDia(no_Atual.tempo_Fim)
                        
        cost = CostCalculator(minutos_Do_Dia_Comecar_Atividade - MinutosDoDiaAcabarAtividadeAnterior, tempo_De_Viagem_Para_A_Atividade, tempo_Para_Realizar_Atividade, False, atividade.data_criacao, values_dict, considerAppointment, considerPriority)

        fronteira.append(No(atividade.idAtividade, cost, tempo_De_Viagem_Para_A_Atividade, hora_De_Chegada_A_Atividade, atividade_Hora_Fim_Real , no_Atual))
        return True

    return False







def atribuir_Atividade_Com_Agendamento(blocoTrabalho: BlocoTrabalho, values_dict: dict, considerAppointment: bool, considerPriority: bool, fronteira: list[No], no_Atual: No, atividade: Atividade, tempo_De_Viagem_Para_A_Atividade: int, tempo_De_Viagem_Para_Voltar_A_Casa: int, hora_De_Chegada_A_Atividade: time, tempo_Para_Realizar_Atividade: int) -> bool:
    
    from Helper import DateTimeTimeParaMinutosDoDia
    
    
    tolerancia_Atividade_Post: int = int (values_dict['WINDOW_TIME_POST'])
    tolerancia_Atividade_Pre: int = int (values_dict['WINDOW_TIME_PRE'])


    max_Time_Atividade: time = adicionar_Minutos_A_DatetimeTime(atividade.agendamento, tolerancia_Atividade_Post)
    ''' o máximo de tempo que pode chegar atrasado '''

    if hora_De_Chegada_A_Atividade <= max_Time_Atividade:
        """Consegue chegar a atividades antes do tempo limite máximo, se não conseguir não a pode realizar"""
        
        hora_Minima_Para_Adiantamento = subtrairMinutosADatetimeTime(atividade.agendamento, tolerancia_Atividade_Pre)

#------------------------------------------------------
        if hora_De_Chegada_A_Atividade >= hora_Minima_Para_Adiantamento:
            """Se chega depois do tempo mínimo, pode começar a trabalhar assim que chegar"""

            atividade_Hora_Fim_Real =  adicionar_Minutos_A_DatetimeTime(hora_De_Chegada_A_Atividade, tempo_Para_Realizar_Atividade)
            ''' hora em que acabaria de realizar a atividade '''

            atividade_Hora_Chegar_Casa = adicionar_Minutos_A_DatetimeTime(atividade_Hora_Fim_Real, tempo_De_Viagem_Para_Voltar_A_Casa)
            ''' hora em que chegaria a casa após a realização da atividade '''

            if atividade_Hora_Chegar_Casa < blocoTrabalho.fim:
                """Se tem tempo de voltar a casa após a realização da atividade"""
                
# Ele aqui chega depois do tempo de adiantamento, ou seja, se sair da ultima atividade, vier direto para esta, chega após a hora de adiantamento, o que lhe permite que comece a trabalhar emidiatamente, como também tem tempo para voltar a casa após a realização da atividade, a atribuição é possivel

                minutos_Do_Dia_Comecar_Atividade = DateTimeTimeParaMinutosDoDia(hora_De_Chegada_A_Atividade)

                tempo_Antre_Atividades = minutos_Do_Dia_Comecar_Atividade - DateTimeTimeParaMinutosDoDia(no_Atual.tempo_Fim)

                cost = CostCalculator(tempo_Antre_Atividades, tempo_De_Viagem_Para_A_Atividade,tempo_Para_Realizar_Atividade, True, atividade.data_criacao, values_dict, considerAppointment, considerPriority)
                
                fronteira.append(No(atividade.idAtividade, cost, tempo_De_Viagem_Para_A_Atividade, hora_De_Chegada_A_Atividade, atividade_Hora_Fim_Real, no_Atual))
                
                return True

#------------------------------------------------------
        else:
            """Se não chegar antes do tempo mínimo, tempo de esperar para começar a realizar a atividade"""


            atividade_Hora_Fim_Real = adicionar_Minutos_A_DatetimeTime(hora_Minima_Para_Adiantamento, tempo_Para_Realizar_Atividade)

            atividade_Hora_Chegar_Casa = adicionar_Minutos_A_DatetimeTime(atividade_Hora_Fim_Real, tempo_De_Viagem_Para_Voltar_A_Casa)

            if atividade_Hora_Chegar_Casa < blocoTrabalho.fim:

# Ele aqui chega antes do tempo de adiantamento, ou seja, se sair da ultima atividade, vier direto para esta, chega antes da hora de adiantamento, o que o obriga a ter de ficar a espera até a hora de adiantamento para poder começar a realizar a atividade, como também tem tempo para voltar a casa após a realização da atividade, a atribuição é possivel
                
                minutos_Do_Dia_Comecar_Atividade = DateTimeTimeParaMinutosDoDia(hora_Minima_Para_Adiantamento)

                tempo_Antre_Atividades = minutos_Do_Dia_Comecar_Atividade - DateTimeTimeParaMinutosDoDia(no_Atual.tempo_Fim)

                cost = CostCalculator(tempo_Antre_Atividades, tempo_De_Viagem_Para_A_Atividade, tempo_Para_Realizar_Atividade, True, atividade.data_criacao, values_dict, considerAppointment, considerPriority)
                                
                                # Adicionar nova Atividade a lista da Fronteira
                fronteira.append(No(atividade.idAtividade, cost, tempo_De_Viagem_Para_A_Atividade, hora_Minima_Para_Adiantamento, atividade_Hora_Fim_Real , no_Atual))
                
                return True

#------------------------------------------------------
    return False




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
        ultimo_No = ultimo_No.pai # type: ignore
            
    # inverter a lista
    path_invertido = path[::-1]
    return path_invertido
