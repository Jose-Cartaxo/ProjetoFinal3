import matplotlib.pyplot as plt
import numpy as np
import sys

import os
from Helper import Distance_Calculator, pedir_Travel_Time, DateTimeTimeParaMinutosDoDia
from Workers import Trabalhador
from Activity import Atividade, Encontrar_Atividade_Por_Id

class Stats:
    def __init__(self, tipo):
        self.tipo = tipo
        self.ativa = 0
        self.total = 1
    
    def maisUmaAtiva(self):
        self.ativa = self.ativa + 1
    
    def maisUma(self):
        self.total = self.total + 1

    def print(self):
        print('Tipo Atividade:',self.tipo, ' ATIVA: ', self.ativa,' TOTAL: ', self.total, ' PERCENT: ', (100/self.total * self.ativa))
        sys.stdout.flush()

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




def AnalisaDadosPorHora(lista_atividades: list[Atividade]) -> list[Stats]:
    """
    Separa as atividades por hora de marcação, guarda a quantidade de atividades que foram realizadas em cada grupo

    Args:
        lista_atividades (list[Atividade]): lista com todas as atividades

    Returns:
        list[Stats]: lista com a quantidade de atividades realizadas por hora
    """

    statsList: list[Stats] = []
    for atividade in lista_atividades:
        found = False
        for stat in statsList:
            if stat.tipo == atividade.agendamento.hour:
                found = True
                stat.maisUma()
                if atividade.estado == 1:
                    stat.maisUmaAtiva()
                break
        if not found:
            new = Stats(atividade.agendamento.hour)
            if atividade.estado == 1:
                new.maisUmaAtiva()
            statsList.append(new)
    
    return statsList


def AnalisaDadosPorSkill(lista_atividades: list[Atividade]) -> list[Stats]:
    statsList: list[Stats] = []
    for atividade in lista_atividades:
        found = False
        for stat in statsList:
            if stat.tipo == atividade.competencia:
                found = True
                stat.maisUma()
                if atividade.estado == 1:
                    stat.maisUmaAtiva()
                break
        if not found:
            new = Stats(atividade.competencia)
            if atividade.estado == 1:
                new.maisUmaAtiva()
            statsList.append(new)
    
    return statsList


def CalcularMediaQuantidadeAtividadesRealizadasPorTrabalhador(listTrabalhadores: list[Trabalhador]):
    total = 0
    for trabalhador in listTrabalhadores:
        local = 0
        for workblock in trabalhador.lista_Blocos_Trabalho:
            total += len(workblock.listaNos)
            local += len(workblock.listaNos)
        trabalhador.quantidadeAtividades = local

    return total / len(listTrabalhadores)



def AnalisaTemposTrabalhadores(listaTrabalhadores: list[Trabalhador], listAtividades: list[Atividade], dicionario_distancias, travel_Time_By_1KM, gmaps):
    tempoTotal = 0
    tempoTotalAtividades = 0
    tempoTotalViagem = 0
    tempoEspera = 0
    tempoNaoUsadoInicio = 0
    tempoNaoUsadoFim = 0
    tempoBlocosNaoUsados = 0
    print('\nQuantidade de minutos gastos em:')
    
    for trabalhador in listaTrabalhadores:
        for workblock in trabalhador.lista_Blocos_Trabalho:
            tempoTotal += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
            
            if len(workblock.listaNos) > 0:

                for node in workblock.listaNos:
                    tempoTotalViagem += node.tempo_Viagem

                # tempo Extra no inicio do dia sem contar com a viagem. Ex. começa as 8:00 uma atividade, o deu dia de trabalho começa as 7:30, mas só demora 10 minutos a lá chegar, ou seja pode sair 20 minutos mais tarde, este tempo vai para o tempo não usado 
                tempoInicioDia = DateTimeTimeParaMinutosDoDia(workblock.listaNos[0].tempo_Inicio) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
                tempoInicioDia -= workblock.listaNos[0].tempo_Viagem
                tempoNaoUsadoInicio += tempoInicioDia

                tempoTotalAtividades += DateTimeTimeParaMinutosDoDia(workblock.listaNos[0].tempo_Fim) - DateTimeTimeParaMinutosDoDia(workblock.listaNos[0].tempo_Inicio)

                for i in range(1, len(workblock.listaNos)):
                    no_atual = workblock.listaNos[i]
                    no_anterior = workblock.listaNos[i - 1]
                    tempoEntreAtividades = DateTimeTimeParaMinutosDoDia(no_atual.tempo_Inicio) - DateTimeTimeParaMinutosDoDia(no_anterior.tempo_Fim)

                    # tempo extra entre viagens, ex. acaba a atividade anterior as 9:00, a próx é as 9:30, e só demora 15 min a lá chegar, 
                    tempoEspera += tempoEntreAtividades - no_atual.tempo_Viagem

                    tempoTotalAtividades += DateTimeTimeParaMinutosDoDia(no_atual.tempo_Fim) - DateTimeTimeParaMinutosDoDia(no_atual.tempo_Inicio)



                tempoFimDia = DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.listaNos[len(workblock.listaNos) - 1].tempo_Fim)

                ultima = Encontrar_Atividade_Por_Id(listAtividades, workblock.listaNos[len(workblock.listaNos) - 1].id)
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
    




def AnalisaTrabalhador(trabalhador: Trabalhador, listaAtividades: list[Atividade], valores_dict):
    nome_txt = "log_" + trabalhador.idTrabalhador + ".txt"
    pasta = "TXT_Logs"
    texto = ""

    atividadesDisponiveis = 0
    atividadesIndisponiveis = 0
    atividadesCompetencia = 0
    atividadesDisponiveisCompetencia = 0
    tempoTotalEntreAtividades = 0
    quantidadeAtividades = 0

    raio = valores_dict['RAIO_ANALISE']
    listaAnalise: list[Atividade] = []
    for atividade in listaAtividades:
        distancia = Distance_Calculator(atividade.latitude, atividade.longitude, trabalhador.latitude, trabalhador.longitude)
        if distancia < raio:
            listaAnalise.append(atividade)

    for atividade in listaAnalise:

        if atividade.estado == 0:
            atividadesDisponiveis += 1
        else:
            atividadesIndisponiveis += 1

        if atividade.competencia in trabalhador.competencia:
            atividadesCompetencia += 1
            if atividade.estado == 0:
                atividadesDisponiveisCompetencia += 1

    tempoTotalViagem = 0


    for workblock in trabalhador.lista_Blocos_Trabalho:

        quantidadeAtividades += len(workblock.listaNos)
        
        if len(workblock.listaNos) > 0:
            for node in workblock.listaNos:
                tempoTotalViagem += node.tempo_Viagem


            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.listaNos[0].tempo_Inicio) - DateTimeTimeParaMinutosDoDia(workblock.inicio)
            for i in range(1, len(workblock.listaNos)):
                no_atual = workblock.listaNos[i]
                no_anterior = workblock.listaNos[i - 1]
                tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(no_atual.tempo_Inicio) - DateTimeTimeParaMinutosDoDia(no_anterior.tempo_Fim)


            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.listaNos[len(workblock.listaNos) - 1].tempo_Fim)
        else:
            tempoTotalEntreAtividades += DateTimeTimeParaMinutosDoDia(workblock.fim) - DateTimeTimeParaMinutosDoDia(workblock.inicio)

    texto = f"""Informacoes:
- ID do trabalhador: {trabalhador.idTrabalhador}
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