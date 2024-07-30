from re import X
from datetime import time


class No:
    quantidadeNos = 0

    def __init__(self, id, custo, tempo_Viagem, tempo_Inicio, tempo_Fim, pai):
        
        self.id: str = id  # id da atividade atribuida a este no
        self.custo: float = custo # custo da realização da atividade
        self.tempo_Viagem: int = tempo_Viagem # tempo em viagem entre Tarefas
        self.tempo_Inicio: time = tempo_Inicio # horas a que começa a realizar a tarefa
        self.tempo_Fim: time = tempo_Fim # horas em que termina a tarefa
        self.pai: No = pai # tarefa raelizada anteriormente
        self.estado: bool = True
        No.quantidadeNos += 1

        if pai:
            self.gen = pai.gen + 1 # o numero da atividade, a 3ª atividade a ser realizada vai ser gen 3
            self.custo_total = pai.custo_total + custo # custo total, o custo desta atividade em especifico mais o total de todas as atividade enteriones
            self.family = pai.family.copy() # copiar a familia da atividade anterior
        else:
            self.gen = 0
            self.custo_total = 0
            self.family = []
        
        self.family.append(id) # adicionar o proprio id a lista de atividades
        

    def printNodeGen(self):
        print('ID: ', self.id, ' custo: ', self.custo,' Totalcusto: ', self.custo_total)
        if self.pai:
            self.pai.printNodeGen()

    # se for maior tem de retornar true
    def __lt__(self, other):

        return self.custo_total > other.custo_total
        # return (self.custo_total / self.gen) > (other.custo_total / other.gen)