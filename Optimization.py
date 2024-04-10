import heapq
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from Clustering import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def Greedy(worker_Activities_Cluster, workBlock, skills_dict, list_workers, values_dict):


    # Fazer a Atribuição para cada bloco de trabalho do trabalhador independentemente.
    frontier = []    
    family = []
    
    worker = Find_Worker_By_Id(list_workers, workBlock.idWorker)
    
    # inicio é o WorkBlock
    heapq.heappush(frontier, Node(workBlock.idWorker, 0, worker.x, worker.y, workBlock.start , family, None))


    while frontier:
        
        print('\n\n  LISTA COMPLETA  ', len(frontier))
        """        
        for node in frontier:
            node.printNode()
        """

        frontier = sorted(frontier)

        current_Node = frontier[0]

        frontier.remove(current_Node)

        print('\n\n  ESCOLHIDO  ')
        current_Node.printNode()

        
        print('\n\n  LISTA COMPLETA  ', len(frontier))
        """
        for node in frontier:
            node.printNode()
        """
        #print('TIPO DO NODE:')
        #print(type(current_Node.end_Time))
        #print(type(workBlock.start))

        current_Time = current_Node.end_Time

        foundActivity = False
        for activity in worker_Activities_Cluster:

            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(values_dict['TRAVEL_TIME'], current_Node.x, current_Node.y, activity.x, activity.y)

            # Converter para DateTime para ser possivel adicioanar
            # datetime_end = datetime.combine(datetime.today(), current_Node.end_Time)

            # Hora de Chegada a Atividade
            datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)
            
            #print('Consigo Chegar a Tempo? Tempo viagem: ', travel_Time_Going, 'Tempo Partida: ', current_Time.time(), ' Tempo Chegada: ', datetime_Arraival.time(), 'Tempo inicio Atividade: ', activity.appointment.time())

            # Verificar se consegue chegar a tempo a Atividade
            if not Belongs_to_Family(current_Node, activity.idActivity) and (datetime_Arraival.time() < activity.appointment.time() or activity.appointment.time() == time(0, 0, 0)):

                # Tempo necessário para se deslocar da Atividade até Casa
                travel_Time_Returning = Travel_Time(values_dict['TRAVEL_TIME'], activity.x, activity.y, worker.x, worker.y)

                # Hora de Chegada a Casa
                time_Required = travel_Time_Going + travel_Time_Returning + skills_dict[activity.skill]

                # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                activity_End_Time = current_Time + timedelta(minutes=time_Required)
                if activity_End_Time < workBlock.finish:
                    foundActivity = True
                    if activity.appointment.time() != time(0, 0, 0):
                        print('ID: ', activity.idActivity, 'Time Before: ', travel_Time_Going)
                        travel_Time_Going = travel_Time_Going * 0.2
                        print('Time After: ', travel_Time_Going)
                    heapq.heappush(frontier, Node(activity.idActivity, travel_Time_Going, activity.x, activity.y, activity_End_Time , current_Node.family, current_Node))
                    # print('Adicionei')
                # else:
                    # print('Não volto a casa')
            
            # else:
                # print('Não chego a tempo')
        if not foundActivity:
            print("A lista está vazia.")
            path = []
            while current_Node:
                path.append(current_Node.id)
                current_Node = current_Node.parent
            return path[::-1]
      
    """  
    print("A lista está vazia.")
    path = []
    while current_Node:
        path.append(current_Node.id)
        current_Node = current_Node.parent
    return path[::-1]



                    if not next_Activities:
                        print("A lista está vazia.")
                        path = []
                        while current_Node:
                            path.append(current_Node.state)
                            current_Node = current_Node.parent
                        return path[::-1]
        raise ValueError(f"Deu merda")
    """

def Belongs_to_Family(node, activity):
    while node:
        if node.id == activity:
            print('Já pertence')
            return True
        node = node.parent
    print('Não pertence')
    return False



