import heapq
from Node import Node
from Workers import Worker

def Greedy(worker_Activities_Cluster, worker):


    # Fazer a Atribuição para cada bloco de trabalho do trabalhador independentemente.

    for workBlock in worker.workBlocks:

            frontier = []    
            family = set()
            
            # inicio é o WorkBlock
            heapq.heappush(frontier, Node(worker.idWorker, 0, workBlock.start , family, None))

            while frontier:

                current_Node = heapq.heappop(frontier)

                start_Time = current_Node.end_Time

                next_Activities = []
                for activity in worker_Activities_Cluster:
                     if

                if current_Node.state == goal_state:
                    path = []
                    while current_Node:
                        path.append(current_Node.state)
                        current_Node = current_Node.parent
                    return path[::-1]
