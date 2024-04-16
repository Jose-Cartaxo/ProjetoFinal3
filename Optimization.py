import heapq
from Activity import Find_Activity_By_Id
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from Clustering import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def Greedy(worker_Activities_Cluster, workBlock, skills_dict, list_workers, values_dict):


    # Fazer a Atribuição para cada bloco de trabalho do trabalhador independentemente.
    frontier = []
    
    worker = Find_Worker_By_Id(list_workers, workBlock.idWorker)
    
    # inicio é o WorkBlock
    heapq.heappush(frontier, Node(workBlock.idWorker, 0, 0, workBlock.start, workBlock.start, None))


    while frontier:
    
        frontier = sorted(frontier)
        current_Node = frontier[0]
        frontier.remove(current_Node)

        current_Time = current_Node.end_Time

        foundActivity = False
        for activity in worker_Activities_Cluster:

            current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)
            if not current_Activity:
                current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)
            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(values_dict['TRAVEL_TIME'], current_Activity.x, current_Activity.y, activity.x, activity.y)
            #print('Tempo viagem de: ', current_Node.id, " ")


            # Hora de Chegada a Atividade
            datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)

            # Verificar se consegue chegar a tempo a Atividade
            if not Belongs_to_Family(current_Node, activity.idActivity):
                if datetime_Arraival.time() < activity.appointment.time() :
                
                    # Tempo necessário para se deslocar da Atividade até Casa
                    travel_Time_Returning = Travel_Time(values_dict['TRAVEL_TIME'], activity.x, activity.y, worker.x, worker.y)

                    # Tempo necessário para a Atividade em si
                    time_Required_for_Activity = skills_dict[activity.skill]

                    # Tempo necessário para chegar a Casa
                    time_Required = time_Required_for_Activity + travel_Time_Returning
                    
                    # Tempo em que acaba a Tarefa
                    activity_End_Time_Real = activity.appointment + timedelta(minutes=time_Required_for_Activity)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    activity_End_Time_Home = activity.appointment + timedelta(minutes=time_Required)
                    if activity_End_Time_Home.time() < workBlock.finish.time():
                        foundActivity = True

                        datetimeAppointment = datetime.combine(datetime.today(), activity.appointment.time())
                        datetimeCurrent_Time = datetime.combine(datetime.today(), current_Time.time())

                        timeSpend = datetimeAppointment - datetimeCurrent_Time
                        timeSpendMinutes = int (timeSpend.total_seconds() // 60)
                        cost = timeSpendMinutes * 0.5

                        heapq.heappush(frontier, Node(id = activity.idActivity, cost = cost, end_Time = activity_End_Time_Real , parent = current_Node))
                



                elif activity.appointment.time() == time(0, 0, 0):

                    # Tempo necessário para se deslocar da Atividade até Casa
                    travel_Time_Returning = Travel_Time(values_dict['TRAVEL_TIME'], activity.x, activity.y, worker.x, worker.y)

                    # Tempo necessário para a Atividade em si
                    time_Required_for_Activity = skills_dict[activity.skill]

                    # Tempo necessário para chegar a Casa
                    time_Required = time_Required_for_Activity + travel_Time_Returning
                    
                    # Tempo em que acaba a Tarefa
                    activity_End_Time_Real = datetime_Arraival + timedelta(minutes=time_Required_for_Activity)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    activity_End_Time_Home = datetime_Arraival + timedelta(minutes=time_Required)

                    if activity_End_Time_Home.time() < workBlock.finish.time():
                        foundActivity = True

                        heapq.heappush(frontier, Node(id = activity.idActivity, cost = travel_Time_Going, end_Time = activity_End_Time_Real , parent = current_Node))



        if not foundActivity:
            print("A lista está vazia.")
            path = []
            while current_Node:
                path.append(current_Node)
                # path.append(current_Node.id)
                current_Node = current_Node.parent
            return path[::-1]
      
    print("A lista2 está vazia.")
    path = []
    while current_Node:
        path.append(current_Node)
        # path.append(current_Node.id)
        current_Node = current_Node.parent
    return path[::-1]



    """  
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
            # print('Já pertence')
            return True
        node = node.parent
    # print('Não pertence')
    return False



