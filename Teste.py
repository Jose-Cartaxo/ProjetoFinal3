
import openpyxl
from random import uniform

# Carregue o arquivo Excel
workbook = openpyxl.load_workbook('WORKERS.xlsx')

# Selecione a planilha desejada
sheet = workbook['WORKERS']

# Itere sobre as células na coluna em que deseja adicionar os valores aleatórios
for cell in sheet['F']:
    # Verifique se a célula não é a primeira linha (cabeçalho)
    if cell.row != 1:
        # Obtenha o valor atual da célula
        valor_atual = cell.value
        # Se o valor existente não for None, adicione um valor aleatório entre -0.1 e 0.1
        if valor_atual is not None:
            valor_aleatorio = uniform(-0.1, 0.1)
            novo_valor = valor_atual + valor_aleatorio
            # Escreva o novo valor de volta na célula
            cell.value = novo_valor

# Salve as alterações no arquivo Excel
workbook.save('WORKERS2.xlsx')



"""

from Clustering import *

print(Travel_Time( 1.1, 44.2747947, 0.5920027, 44.328734, 0.5913167))

print(Travel_Time( 1.1, 44.3, 0.6, 44.328734, 0.5913167))

"""


"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Seus dados de pontos e cores
x_values = [1, 2, 3, 4, 5]
y_values = [2, 3, 4, 5, 6]
cores_pontos = ['red', 'black', 'green', 'blue', 'orange']

# Definindo coordenadas de início e fim dos vetores
x_start = [1, 2, 3]  # coordenadas x do ponto inicial
y_start = [2, 3, 4]  # coordenadas y do ponto inicial
x_end = [2, 3, 4]    # coordenadas x do ponto final
y_end = [3, 4, 5]    # coordenadas y do ponto final
cores_vetores = ['black', 'blue', 'green']  # cores dos vetores

# Plotando o gráfico de dispersão
plt.scatter(x_values, y_values, c=cores_pontos)
plt.title('Gráfico de Coordenadas das Tarefas')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')

# Adicionando os vetores ao gráfico
for i in range(len(x_start)):
    plt.arrow(x_start[i], y_start[i], x_end[i] - x_start[i], y_end[i] - y_start[i],
              color=cores_vetores[i], width=0.05, head_width=0.3, length_includes_head=True)

# Adicionando legenda
legend_elements = [
    Line2D([], [], marker='o', color='red', label='Não contabilizadas', linestyle='None'),
    Line2D([], [], marker='o', color='black', label='Ponto Partida', linestyle='None'),
    Line2D([], [], marker='o', color='green', label='Contabilizadas', linestyle='None'),
    Line2D([], [], marker='o', color='blue', label='Atribuidas', linestyle='None'),
    Line2D([], [], color='black', linewidth=1, label='Vetores')
]

plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

# Exibindo o gráfico
plt.show()

"""


"""

import heapq

class Node:
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value > other.value  # Retornar True se o valor de self for maior que o valor de other

lista = []
node1 = Node(10)
node2 = Node(20)
heapq.heappush(lista, node1)
heapq.heappush(lista, node2)

current_Node = heapq.heappop(lista)


print(current_Node.value)  

"""