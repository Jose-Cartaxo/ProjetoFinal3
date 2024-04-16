import heapq
from Activity import Find_Activity_By_Id
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from Clustering import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def CostCalculator(total_time_spend, travel_time, activity_time, values_dict):
    travel_Time_By_1KM = values_dict['TRAVEL_TIME']
    travel_Consumption_By_Hour = values_dict['GAS_CONSUMPTION']
    travel_Consumption_By_Min = travel_Consumption_By_Hour // 60
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr // 60
    labor_Gainz_Hr = values_dict['LABOR_GAINS']
    labor_Gainz_Min = labor_Gainz_Hr // 60

    cost = -((total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price))

    cost = cost + (activity_time * labor_Gainz_Min)

    return cost


def Belongs_to_Family(node, activity):
    while node:
        if node.id == activity:
            # print('Já pertence')
            return True
        node = node.parent
    # print('Não pertence')
    return False



def Greedy(worker_Activities_Cluster, workBlock, skills_dict, list_workers, values_dict):

    # dia de "hoje"
    current_DateTime = datetime.now()

    # "extermidades" de cada "ramo"
    frontier = []
    
    time_starting = datetime.combine(current_DateTime.date(), workBlock.start)
    # inicio é o WorkBlock
    heapq.heappush(frontier, Node(workBlock.idWorker, 0, 0,time_starting, time_starting, None))


    while frontier:
    
        travel_Time_By_1KM = values_dict['TRAVEL_TIME']

        tolerance_For_Activity_Post = values_dict['WINDOW_TIME_POST']
        tolerance_For_Activity_Pre = values_dict['WINDOW_TIME_PRE']

        # organizar as "extermidades" de cada "ramo" por custo
        frontier = sorted(frontier)

        # pegar no ramo com menor custo
        current_Node = frontier[0]

        #remover o ramo como extermidade (depois adiciono as novas "extermidades" provenientes desta "extermidade", se não existirem novas extermidades, solução encontrada)
        frontier.remove(current_Node)

        current_Time = current_Node.end_Time

        foundActivity = False
        for activity in worker_Activities_Cluster:

            current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

            if not current_Activity:
                current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)
            
            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, activity.x, activity.y)


            # Hora de Chegada a Atividade
            datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)

            # Verificar se consegue chegar a tempo a Atividade
            if not Belongs_to_Family(current_Node, activity.idActivity):

                time_Tolerance_For_Activity_Post = timedelta(minutes=tolerance_For_Activity_Post)
                time_Tolerance_For_Activity_Pre = timedelta(minutes=tolerance_For_Activity_Pre)
                max_Time_Activity = activity.appointment + time_Tolerance_For_Activity_Post
                min_Time_Activity = activity.appointment - time_Tolerance_For_Activity_Pre

                # Está antes do limite máximo para comparecer.
                if datetime_Arraival.time() < max_Time_Activity.time():

                    
                    # Ele aqui, se sair da Atividade anterior e vier diretamente para a atual está dentro do espaço de tempo de tolerância, ou seja, pode vir e começar a Trabalhar emidiatamente, sem tempos de espera para o inicio
                    if datetime_Arraival.time() > min_Time_Activity.time():

                        # Tempo necessário para se deslocar da Atividade até Casa
                        travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y)

                        # Tempo necessário para a Atividade em si
                        time_Required_for_Activity = skills_dict[activity.skill]

                        # Tempo necessário para chegar a Casa
                        time_Required = time_Required_for_Activity + travel_Time_Returning
                        
                        # Tempo em que acaba a Tarefa
                        activity_End_Time_Real = datetime_Arraival + timedelta(minutes=time_Required_for_Activity)

                        # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                        activity_End_Time_Home = datetime_Arraival + timedelta(minutes=time_Required)

                        if activity_End_Time_Home.time() < workBlock.finish:

                            foundActivity = True

                            # o appointment da Atividade agora em date time, com a data de dia de "hoje", a hora seria a correta.


                            todaydatetimeAppointment = datetime.combine(current_DateTime.date(), activity.appointment.time())

                            
                            timeSpend = todaydatetimeAppointment - current_DateTime

                            timeSpendMinutes = int (timeSpend.total_seconds() // 60)
                            # timeSpendMinutes = timeSpendMinutes - travel_Time_Going

                            # calcular os custos, isto é, o custo do trabalhador, mais o custo do automóvel
                            cost = CostCalculator(timeSpendMinutes, travel_Time_Going, time_Required_for_Activity, values_dict)

                            heapq.heappush(frontier, Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real, current_Node))

                            


                    else:
                        
                        # Tempo necessário para se deslocar da Atividade até Casa
                        travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y)

                        # Tempo necessário para a Atividade em si
                        time_Required_for_Activity = skills_dict[activity.skill]

                        # Tempo necessário para chegar a Casa
                        time_Required = time_Required_for_Activity + travel_Time_Returning
                        
                        # Tempo em que acaba a Tarefa
                        activity_End_Time_Real = activity.appointment + timedelta(minutes=time_Required_for_Activity)

                        # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                        activity_End_Time_Home = activity.appointment + timedelta(minutes=time_Required)


                        if activity_End_Time_Home.time() < workBlock.finish:
                            foundActivity = True

                            
                            todaydatetimeAppointment = datetime.combine(current_DateTime.date(), activity.appointment.time())

                            datetimeAppointment = datetime.combine(current_Time.date(), activity.appointment.time())
                            

                            timeSpend = datetimeAppointment - current_DateTime
                            timeSpendMinutes = int (timeSpend.total_seconds() // 60)


                            cost = CostCalculator(timeSpendMinutes, travel_Time_Going, time_Required_for_Activity, values_dict)

                            heapq.heappush(frontier, Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real , current_Node))



                elif activity.appointment.time() == time(0, 0, 0):

                    # Tempo necessário para se deslocar da Atividade até Casa
                    travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y)

                    # Tempo necessário para a Atividade em si
                    time_Required_for_Activity = skills_dict[activity.skill]

                    # Tempo necessário para chegar a Casa
                    time_Required = time_Required_for_Activity + travel_Time_Returning
                    
                    # Tempo em que acaba a Tarefa
                    activity_End_Time_Real = datetime_Arraival + timedelta(minutes=time_Required_for_Activity)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    activity_End_Time_Home = datetime_Arraival + timedelta(minutes=time_Required)

                    if activity_End_Time_Home.time() < workBlock.finish:
                        foundActivity = True

                        heapq.heappush(frontier, Node(id = activity.idActivity, cost = travel_Time_Going, travel_Time = travel_Time_Going, start_Time = datetime_Arraival, end_Time = activity_End_Time_Real , parent = current_Node))



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



