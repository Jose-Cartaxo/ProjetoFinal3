import matplotlib.pyplot as plt
import numpy as np

import os
from Workers import Worker
from Activity import Activity, Find_Activity_By_Id
from Helper import Distance_Calculator, pedir_Travel_Time
from Optimization import DateTimeTimeParaMinutosDoDia

class Stats:
    def __init__(self, tipo):
        self.tipo = tipo
        self.active = 0
        self.total = 1
    
    def plusOneActive(self):
        self.active = self.active + 1
    
    def plusOne(self):
        self.total = self.total + 1

    def print(self):
        print('Tipo Atividade:',self.tipo, ' ATIVA: ', self.active,' TOTAL: ', self.total, ' PERCENT: ', (100/self.total * self.active))

    def __lt__(self, other):
        return self.tipo < other.tipo

class WorkBlockStats:
    workblockquantidade = 0
    workblockquantidademanha = 0
    workblockquantidadetarde = 0
    def __init__(self, tipo, quantidade):
        self.tipo = tipo
        self.quantidade = quantidade
        WorkBlockStats.workblockquantidade += 1
        if tipo == 'manha' :
            WorkBlockStats.workblockquantidademanha += 1
            self.id = WorkBlockStats.workblockquantidademanha
        else:
            WorkBlockStats.workblockquantidadetarde += 1
            self.id = WorkBlockStats.workblockquantidadetarde




def DataAnalyticsByHour(listActivities: list[Activity]):
    statsList = []
    for activity in listActivities:
        found = False
        for stat in statsList:
            if stat.tipo == activity.agendamento.hour:
                found = True
                stat.plusOne()
                if activity.state == 1:
                    stat.plusOneActive()
                break
        if not found:
            new = Stats(activity.agendamento.hour)
            if activity.state == 1:
                new.plusOneActive()
            statsList.append(new)
    
    return statsList


def DataAnalyticsBySkill(listActivities: list[Activity]):
    statsList = []
    for activity in listActivities:
        found = False
        for stat in statsList:
            if stat.tipo == activity.competencia:
                found = True
                stat.plusOne()
                if activity.state == 1:
                    stat.plusOneActive()
                break
        if not found:
            new = Stats(activity.competencia)
            if activity.state == 1:
                new.plusOneActive()
            statsList.append(new)
    
    return statsList


def CalcularMediaQuantidadeAtividadesRealizadasPorTrabalhador(listTrabalhadores: list[Worker]):
    total = 0
    for trabalhador in listTrabalhadores:
        local = 0
        for workblock in trabalhador.work_Blocks:
            total += len(workblock.listNodes)
            local += len(workblock.listNodes)
        trabalhador.quantidadeAtividades = local

    return total / len(listTrabalhadores)



def AnalisaTemposTrabalhadores(listaTrabalhadores: list[Worker], listAtividades: list[Activity], dicionario_distancias, travel_Time_By_1KM, gmaps):
    tempoTotal = 0
    tempoTotalAtividades = 0
    tempoTotalViagem = 0
    tempoEspera = 0
    tempoNaoUsadoInicio = 0
    tempoNaoUsadoFim = 0
    tempoBlocosNaoUsados = 0
    print('\nQuantidade de minutos gastos em:')
    
    for trabalhador in listaTrabalhadores:
        for workblock in trabalhador.work_Blocks:
            tempoTotal += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
            
            if len(workblock.listNodes) > 0:

                for node in workblock.listNodes:
                    tempoTotalViagem += node.travel_Time

                # tempo Extra no inicio do dia sem contar com a viagem. Ex. começa as 8:00 uma atividade, o deu dia de trabalho começa as 7:30, mas só demora 10 minutos a lá chegar, ou seja pode sair 20 minutos mais tarde, este tempo vai para o tempo não usado 
                tempoInicioDia = DateTimeTimeParaMinutosDoDia(workblock.listNodes[0].start_Time) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
                tempoInicioDia -= workblock.listNodes[0].travel_Time
                tempoNaoUsadoInicio += tempoInicioDia

                tempoTotalAtividades += DateTimeTimeParaMinutosDoDia(workblock.listNodes[0].end_Time) - DateTimeTimeParaMinutosDoDia(workblock.listNodes[0].start_Time)

                for i in range(1, len(workblock.listNodes)):
                    no_atual = workblock.listNodes[i]
                    no_anterior = workblock.listNodes[i - 1]
                    tempoEntreAtividades = DateTimeTimeParaMinutosDoDia(no_atual.start_Time) - DateTimeTimeParaMinutosDoDia(no_anterior.end_Time)

                    # tempo extra entre viagens, ex. acaba a atividade anterior as 9:00, a próx é as 9:30, e só demora 15 min a lá chegar, 
                    tempoEspera += tempoEntreAtividades - no_atual.travel_Time

                    tempoTotalAtividades += DateTimeTimeParaMinutosDoDia(no_atual.end_Time) - DateTimeTimeParaMinutosDoDia(no_atual.start_Time)



                tempoFimDia = DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.listNodes[len(workblock.listNodes) - 1].end_Time)

                ultima = Find_Activity_By_Id(listAtividades, workblock.listNodes[len(workblock.listNodes) - 1].id)
                ultimaViagem = pedir_Travel_Time(dicionario_distancias, travel_Time_By_1KM, ultima.latitude, ultima.longitude, workblock.latitude, workblock.longitude, gmaps) # type: ignore
                
                tempoTotalViagem += ultimaViagem

                tempoFimDia -= ultimaViagem

                tempoNaoUsadoFim += tempoFimDia
            else:
                tempoBlocosNaoUsados += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.inicio)

    print('tempoTotal: ', tempoTotal, '(Tempo total disponivel em blocos de trabalho)')
    print('tempoTotalAtividades: ', tempoTotalAtividades, '(Tempo utilizado a realizar atividades)')
    print('tempoTotalViagem: ', tempoTotalViagem,'(Tempo gasto a realizar viagens)')
    print('tempoEspera: ', tempoEspera,'(Tempo gasto a espera da hora para realizar uma atividade)')
    print('tempoNaoUsadoInicio: ', tempoNaoUsadoInicio,'(Tempo não usado no inicio do dia (o trabalhador pode sair mais tarde de casa))')
    print('tempoNaoUsadoFim: ', tempoNaoUsadoFim,'(Tempo não usado no fim do dia (o trabalhador pode ir mais cedo para casa))')
    print('tempoBlocosNaoUsados: ', tempoBlocosNaoUsados,'(blocos de trabalhado que não conseguiram obter nenhuma atribuição)')
    print('')
    




def AnalisaTrabalhador(trabalhador: Worker, listaAtividades: list[Activity], valores_dict):
    nome_txt = "log_" + trabalhador.idWorker + ".txt"
    pasta = "TXT_Logs"
    texto = ""

    atividadesDisponiveis = 0
    atividadesIndisponiveis = 0
    atividadesCompetencia = 0
    atividadesDisponiveisCompetencia = 0
    tempoTotalEntreAtividades = 0
    quantidadeAtividades = 0

    raio = valores_dict['RAIO_ANALISE']
    listaAnalise: list[Activity] = []
    for atividade in listaAtividades:
        distancia = Distance_Calculator(atividade.latitude, atividade.longitude, trabalhador.latitude, trabalhador.longitude)
        if distancia < raio:
            listaAnalise.append(atividade)

    for atividade in listaAnalise:

        if atividade.state == 0:
            atividadesDisponiveis += 1
        else:
            atividadesIndisponiveis += 1

        if atividade.competencia in trabalhador.competencia:
            atividadesCompetencia += 1
            if atividade.state == 0:
                atividadesDisponiveisCompetencia += 1

    tempoTotalViagem = 0


    for workblock in trabalhador.work_Blocks:

        quantidadeAtividades += len(workblock.listNodes)
        
        if len(workblock.listNodes) > 0:
            for node in workblock.listNodes:
                tempoTotalViagem += node.travel_Time


            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.listNodes[0].start_Time) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
            for i in range(1, len(workblock.listNodes)):
                no_atual = workblock.listNodes[i]
                no_anterior = workblock.listNodes[i - 1]
                tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(no_atual.start_Time) - DateTimeTimeParaMinutosDoDia(no_anterior.end_Time)


            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.listNodes[len(workblock.listNodes) - 1].end_Time)
        else:
            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.inicio)

    texto = f"""Informacoes:
- ID do trabalhador: {trabalhador.idWorker}
- Quantidade atividades realizadas: {quantidadeAtividades}

- Raio: {raio}

- Quantidade de atividades no seu raio: {len(listaAnalise)}
- Quantidade de atividades no seu raio disponiveis: {atividadesDisponiveis}
- Quantidade de atividades no seu raio indisponiveis: {atividadesIndisponiveis}

- Quantidade de atividades no seu raio com competencia: {atividadesCompetencia}
- Quantidade de atividades no seu raio disponiveis com competencia: {atividadesDisponiveisCompetencia}

- Tempo em Viagem: {tempoTotalViagem}
- Tempo de Sobra: {tempoTotalEntreAtividades}
"""
    
    caminho_arquivo = os.path.join(pasta, nome_txt)

    # Abre o arquivo para escrita e escreve o texto
    with open(caminho_arquivo, 'w') as arquivo:
        arquivo.write(texto)