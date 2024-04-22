from re import X


class Node:
    def __init__(self, id, cost, travel_Time, start_Time, end_Time, parent):
        
        self.id = id  # id da atividade atribuida a este no
        self.cost = cost # custo da realização da atividade
        self.travel_Time = travel_Time # tempo em viagem entre Tarefas
        self.start_Time = start_Time # horas a que começa a realizar a tarefa
        self.end_Time = end_Time # horas em que termina a tarefa
        self.parent = parent # tarefa raelizada anteriormente

        if parent:
            self.gen = parent.gen + 1 # o numero da atividade, a 3ª atividade a ser realizada vai ser gen 3
            self.total_cost = parent.total_cost + cost # custo total, o custo desta atividade em especifico mais o total de todas as atividade enteriones
            self.family = parent.family.copy() # copiar a familia da atividade anterior
        else:
            self.gen = 0
            self.total_cost = 0
            self.family = []
        
        self.family.append(id) # adicionar o proprio id a lista de atividades
        

    def printNode(self):
        print('ID: ', self.id, ' Cost: ', self.total_cost, ' end_Time: ', self.end_Time, ' Gen: ', self.gen)

    # se for maior tem de retornar true
    def __lt__(self, other):
        if self.gen == 0:
            return False
        if other.gen == 0:
            return True
        
        # return self.total_cost < other.total_cost 
        return (self.total_cost / self.gen) < (other.total_cost / other.gen)