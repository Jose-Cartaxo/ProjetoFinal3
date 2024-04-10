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