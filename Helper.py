from Activity import *

def solicitar_input(min, max):
    while True:
        try:
            valor = int(input('Por favor, insira um número entre ' + str(min) + ' e ' + str(max) +': '))
            if min <= valor <= max:
                return valor
            else:
                print("Valor fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número inteiro.")


def pedir_s_n():
    while True:
        inp = input('"s" para sim, "n" para não: ')
        if inp != 's' and inp != 'n':
            print('Input errado! Tente novamente.')
        else:
            if inp == 'n':
                return False
            return True
        

def activitiesToState1(nodes, list_activities):
    for node in nodes:
        activity = Find_Activity_By_Id(list_activities, node.id)
        if activity:
            activity.state = 1