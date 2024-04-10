import heapq
from Node import Node
from Workers import Worker
from Clustering import Travel_Time
from Main import skills_dict

def Greedy(worker_Activities_Cluster, worker):


    # Fazer a Atribuição para cada bloco de trabalho do trabalhador independentemente.

    for workBlock in worker.workBlocks:

            frontier = []    
            family = set()
            
            # inicio é o WorkBlock
            heapq.heappush(frontier, Node(worker.idWorker, 0, workBlock.start , family, None))

            while frontier:
                current_Node = heapq.heappop(frontier)

                current_Time = current_Node.end_Time

                next_Activities = []
                for activity in worker_Activities_Cluster:

                    # Tempo necessário para se deslocar até a Atividade
                    travel_Time_Going = Travel_Time(workBlock.x, workBlock.y, activity.x, activity.y)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    travel_Time_Returning = Travel_Time(workBlock.x, workBlock.y, activity.x, activity.y)

                    time_Required = travel_Time_Going + travel_Time_Returning + skills_dict[activity.skill]

                    activity_End_Time = current_Time + time_Required
                    if current_Time 

                if current_Node.state == goal_state:
                    path = []
                    while current_Node:
                        path.append(current_Node.state)
                        current_Node = current_Node.parent
                    return path[::-1]
