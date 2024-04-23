import heapq
from Activity import Find_Activity_By_Id
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from Clustering import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd
import random

def CostCalculator(total_time_spend, travel_time, activity_time, values_dict):

    # print('Total: ', total_time_spend, ' Viagem: ', travel_time, ' Atividade: ', activity_time)
    travel_Consumption_By_Hour = values_dict['GAS_CONSUMPTION']
    travel_Consumption_By_Min = travel_Consumption_By_Hour / 60
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60
    labor_Gainz_Hr = values_dict['LABOR_GAINS']
    labor_Gainz_Min = labor_Gainz_Hr / 60
    # print('gas_Price: ', gas_Price, ' labor_Price_Min: ', labor_Gainz_Min, ' labor_Gainz_Min: ', labor_Price_Min)

    # print('Total: ', (total_time_spend * labor_Price_Min), ' Viagem: ', ((travel_time * travel_Consumption_By_Min) * gas_Price), ' Atividade: ', (activity_time * labor_Gainz_Min))

    cost = ((total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price))
    #print('Gasto Trabalho: ' + str(total_time_spend * labor_Price_Min) + ', Gasto Viagem: ' + str((travel_time * travel_Consumption_By_Min) * gas_Price) + ', Total: ' + str(cost))
    # cost = cost - (activity_time * labor_Gainz_Min)
    # print('Custo: ', cost)
    # print('\n\n\n\n')
    return cost


def CostCalculatorBackHome(total_time_spend, travel_time, values_dict):

    # print('Total: ', total_time_spend, ' Viagem: ', travel_time, ' Atividade: ', activity_time)
    travel_Consumption_By_Hour = values_dict['GAS_CONSUMPTION']
    travel_Consumption_By_Min = travel_Consumption_By_Hour / 60
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60
    # print('gas_Price: ', gas_Price, ' labor_Price_Min: ', labor_Gainz_Min, ' labor_Gainz_Min: ', labor_Price_Min)

    # print('Total: ', (total_time_spend * labor_Price_Min), ' Viagem: ', ((travel_time * travel_Consumption_By_Min) * gas_Price), ' Atividade: ', (activity_time * labor_Gainz_Min))

    cost = (total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price)

    # cost = cost - (activity_time * labor_Gainz_Min)
    # print('Custo: ', cost)
    # print('\n\n\n\n')
    # print(cost)
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


    # for act in worker_Activities_Cluster:
        # act.printActivity()

    # print("Enter para continuar...")
    # input()

    # random.shuffle(worker_Activities_Cluster)
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
        

        frontier = sorted(frontier)
       
        

        
        

        '''

        # organizar as "extermidades" de cada "ramo" por custo
        
        # pegar no ramo com menor custo
        current_Node = frontier[0]
        print('\n\n\n RAMOS Extermidades')
        for node in frontier:
            print('Extermidade - ' + str(node.id))
            current_Node = node
            while current_Node:
                current_Node.printNode()
                current_Node = current_Node.parent

        
        print('\n Escolhido \n' + str(frontier[0].id))

        while current_Node:
            current_Node.printNode()
            current_Node = current_Node.parent
        

        
        print("Enter para continuar...")
        input()
        
        '''


        current_Node = frontier[0]
        #remover o ramo como extermidade (depois adiciono as novas "extermidades" provenientes desta "extermidade", se não existirem novas extermidades, solução encontrada)
        # frontier.remove(current_Node)

        current_Time = current_Node.end_Time
        foundActivity = False

        '''
        print("Enter para continuar...")
        input()
        '''
        travel_Time_Returning = 0
        for activity in worker_Activities_Cluster:

            current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

            if not current_Activity:
                current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)
            
            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, activity.x, activity.y) # type: ignore

            # Tempo necessário para se deslocar da Atividade até Casa
            travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y)

            # Hora de Chegada a Atividade
            datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)

            # Verificar se consegue chegar a tempo a Atividade
            if not Belongs_to_Family(current_Node, activity.idActivity):

                time_Tolerance_For_Activity_Post = timedelta(minutes=tolerance_For_Activity_Post)
                # max_Time_Activity = activity.appointment + time_Tolerance_For_Activity_Post
                max_Time_Activity = datetime.combine(datetime.now().date(), activity.appointment) + time_Tolerance_For_Activity_Post


                time_Tolerance_For_Activity_Pre = timedelta(minutes=tolerance_For_Activity_Pre)
                # min_Time_Activity = activity.appointment - time_Tolerance_For_Activity_Pre
                min_Time_Activity = datetime.combine(datetime.now().date(), activity.appointment) - time_Tolerance_For_Activity_Pre
                
                
                # print('\n\n\n')
                # print(datetime_Arraival.time())
                # print('<')
                # print(max_Time_Activity.time())
                # print('\n')
                # Está antes do limite máximo para comparecer.
                if datetime_Arraival.time() < max_Time_Activity.time():
                    # print('Passou')

                    
                    # Ele aqui, se sair da Atividade anterior e vier diretamente para a atual está dentro do espaço de tempo de tolerância, ou seja, pode vir e começar a Trabalhar emidiatamente, sem tempos de espera para o inicio
                    if datetime_Arraival.time() > min_Time_Activity.time():
                        

                        # Tempo necessário para a Atividade em si
                        time_Required_for_Activity = skills_dict[activity.skill]
                        # print('tempo para realizar a tarefa: ', time_Required_for_Activity)


                        # Tempo necessário para chegar a Casa
                        time_Required = time_Required_for_Activity + travel_Time_Returning
                        # print('tempo total: ', time_Required)
                        

                        # Tempo em que acaba a Tarefa
                        activity_End_Time_Real = datetime_Arraival + timedelta(minutes=time_Required_for_Activity)
                        # print('tempo fim tarefa: ', activity_End_Time_Real)


                        # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                        activity_End_Time_Home = datetime_Arraival + timedelta(minutes=time_Required)
                        # print('tempo chegada a casa: ', activity_End_Time_Home)
                        
                        # print(activity_End_Time_Home.time())
                        # print('<')
                        # print(workBlock.finish)

                        if activity_End_Time_Home.time() < workBlock.finish:
                            foundActivity = True

                            # o appointment da Atividade agora em date time, com a data de dia de "hoje", a hora seria a correta.

                            # print(todaydatetimeAppointment)
                            # print(activity.appointment)
                            # print(activity.appointment.time())
                            # print('-')
                            # print(current_DateTime)

                            # timeSpendMinutes = timeSpendMinutes - travel_Time_Going

                            # calcular os custos, isto é, o custo do trabalhador, mais o custo do automóvel

                            # print('Ação instantanea')

                            minutesDayCurrent = current_Node.end_Time.time().hour * 60 + current_Node.end_Time.time().minute

                            minutesDayStart = datetime_Arraival.time().hour * 60 + datetime_Arraival.time().minute

                            # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                            cost = CostCalculator(minutesDayStart - minutesDayCurrent, travel_Time_Going, time_Required_for_Activity, values_dict)
                            # print('Entrei no inicio da Atividade: ',activity.idActivity, ', Cost: ', cost)

                            heapq.heappush(frontier, Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real, current_Node))

                            


                    else:
                        # Tempo necessário para a Atividade em si
                        time_Required_for_Activity = skills_dict[activity.skill]

                        # Tempo necessário para chegar a Casa
                        time_Required = time_Required_for_Activity + travel_Time_Returning
                        
                        # Tempo em que acaba a Tarefa
                        activity_End_Time_Real = min_Time_Activity + timedelta(minutes=time_Required_for_Activity)

                        # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                        activity_End_Time_Home = min_Time_Activity + timedelta(minutes=time_Required)


                        if activity_End_Time_Home.time() < workBlock.finish:
                            foundActivity = True

                            
                            minutesDayCurrent = current_Node.end_Time.time().hour * 60 + current_Node.end_Time.time().minute

                            minutesDayStart = min_Time_Activity.time().hour * 60 + min_Time_Activity.time().minute

                            #print('Ação demorada')
                            
                            # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)

                            cost = CostCalculator(minutesDayStart - minutesDayCurrent, travel_Time_Going, time_Required_for_Activity, values_dict)
                            
                            # print('Entrei a meio da Atividade: ',activity.idActivity, ', Cost: ', cost)
                            
                            heapq.heappush(frontier, Node(activity.idActivity, cost, travel_Time_Going, min_Time_Activity, activity_End_Time_Real , current_Node))



                elif activity.appointment == time(0, 0):
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


                        minutesDayCurrent = current_Node.end_Time.time().hour * 60 + current_Node.end_Time.time().minute

                        minutesDayStart = datetime_Arraival.time().hour * 60 + datetime_Arraival.time().minute

                        # print('Brincadeira sem hora limite')
                        
                        # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                        
                        cost = CostCalculator(minutesDayStart - minutesDayCurrent, travel_Time_Going, time_Required_for_Activity, values_dict)

                        # print('Entrei ATOA: ',activity.idActivity, ', Cost: ', cost)


                        heapq.heappush(frontier, Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real , current_Node))



        if not foundActivity:
            if(current_Node.state == 0):
                path = []
                while current_Node:
                    # print(current_Node.gen)
                    path.append(current_Node)
                    # path.append(current_Node.id)
                    current_Node = current_Node.parent
                return path[::-1]

            #print(current_Node.end_Time.time().hour)
            minutesNode = current_Node.end_Time.time().hour * 60 + current_Node.end_Time.time().minute
            minutesBlock = workBlock.finish.hour * 60 + workBlock.finish.minute 
            current_Node.cost += CostCalculatorBackHome(abs(minutesBlock - minutesNode), travel_Time_Returning, values_dict)
            current_Node.state = 0
        else:
            # print('!_!_!_REMOVEU_!_!_!')
            frontier.remove(current_Node)
           
      
    # print("A lista2 está vazia.")
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



