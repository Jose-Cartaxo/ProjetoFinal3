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
    
    worker = Find_Worker_By_Id(list_workers, workBlock.idWorker)
    
    # inicio é o WorkBlock
    heapq.heappush(frontier, Node(workBlock.idWorker, 0, worker.x, worker.y, workBlock.start , None))


    while frontier:
    
        frontier = sorted(frontier)
        current_Node = frontier[0]
        frontier.remove(current_Node)

        current_Time = current_Node.end_Time

        foundActivity = False
        for activity in worker_Activities_Cluster:

            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(values_dict['TRAVEL_TIME'], current_Node.x, current_Node.y, activity.x, activity.y)

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

                        print('Diferença entre: ', activity.appointment.time(), ' e: ', current_Time.time(),' igual a: ', timeSpend)

                        print("Diferença de tempo:", timeSpend)
                        print("Horas:", timeSpend.seconds // 3600)  # Obtém apenas as horas
                        print("Minutos:", timeSpend.seconds // 60)


                        heapq.heappush(frontier, Node(id = activity.idActivity, cost = cost, x = activity.x, y = activity.y, end_Time = activity_End_Time_Real , parent = current_Node))
                        activity.state = 1

                



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

                        heapq.heappush(frontier, Node(id = activity.idActivity, cost = travel_Time_Going, x = activity.x, y = activity.y, end_Time = activity_End_Time_Real , parent = current_Node))
                        activity.state = 1



        if not foundActivity:
            print("A lista está vazia.")
            path = []
            while current_Node:
                path.append(current_Node)
                # path.append(current_Node.id)
                current_Node = current_Node.parent
            return path[::-1]
      
    print("A lista está vazia.")
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



