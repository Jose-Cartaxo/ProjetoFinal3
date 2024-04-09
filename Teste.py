import heapq

class Node:
    def __init__(self, state, cost, parent):
        self.state = state
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

def uniform_cost_search(initial_state, goal_state, graph):
    frontier = []
    explored = set()

    heapq.heappush(frontier, Node(initial_state, 0, None))

    while frontier:
        current_node = heapq.heappop(frontier)

        if current_node.state == goal_state:
            path = []
            while current_node:
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1]

        explored.add(current_node.state)

        for neighbor, cost in graph[current_node.state]:
            if neighbor not in explored:
                heapq.heappush(frontier, Node(neighbor, current_node.cost + cost, current_node))

    return None

# Exemplo de utilização:
graph = {
    'A': [('B', 1), ('C', 5)],
    'B': [('A', 1), ('D', 3), ('E', 6)],
    'C': [('A', 5), ('F', 7)],
    'D': [('B', 3)],
    'E': [('B', 6), ('G', 9)],
    'F': [('C', 7)],
    'G': [('E', 9)]
}

initial_state = 'A'
goal_state = 'G'

path = uniform_cost_search(initial_state, goal_state, graph)
if path:
    print("Caminho encontrado:", path)
else:
    print("Caminho não encontrado.")
