from re import X
from typing import Optional 
from datetime import time


class No:
    quantidadeNos = 0

    def __init__(self, id: str, lucro: float, tempo_Viagem: int, tempo_Inicio: time, tempo_Fim: time, pai : Optional['No']):
        
        self.id: str = id                      # id da atividade atribuida a este no
        self.lucro: float = lucro              # custo da realização da atividade
        self.tempo_Viagem: int = tempo_Viagem  # tempo em viagem entre Tarefas
        self.tempo_Inicio: time = tempo_Inicio # horas a que começa a realizar a tarefa
        self.tempo_Fim: time = tempo_Fim       # horas em que termina a tarefa
        self.pai: No | None = pai              # tarefa raelizada anteriormente
        self.estado: bool = True               # estado terminado ou não
        No.quantidadeNos += 1                  

        if pai:
            self.gen: int = pai.gen + 1 # o numero da atividade, a 3ª atividade a ser realizada vai ser gen 3
            self.lucro_total: float  = pai.lucro_total + lucro # custo total, o custo desta atividade em especifico mais o total de todas as atividade enteriones
            self.familia: list[str] = pai.familia.copy() # copiar a familia da atividade anterior
        else:
            self.gen: int = 0
            self.lucro_total: float  = 0
            self.familia: list[str]  = []
        
        self.familia.append(id) # adicionar o proprio id a lista de atividades
        

    def printNodeGen(self):
        print('ID: ', self.id, ' custo: ', self.lucro,' Totalcusto: ', self.lucro_total)
        if self.pai:
            self.pai.printNodeGen()

    # se for maior tem de retornar true
    def __lt__(self, other: 'No'):

        return self.lucro_total > other.lucro_total
        # return (self.custo_total / self.gen) > (other.custo_total / other.gen)