import heapq
from Activity import Find_Activity_By_Id
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from Clustering import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def CostCalculator(total_time_spend, travel_time, appointment, creationDate, values_dict, considerAppointment, considerPriority):

    # print('Total: ', total_time_spend, ' Viagem: ', travel_time, ' Atividade: ', activity_time)

    travel_Consumption_By_Min = values_dict['GAS_CONSUMPTION'] # 
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60

    # print('gas_Price: ', gas_Price, ' labor_Price_Min: ', labor_Gainz_Min, ' labor_Gainz_Min: ', labor_Price_Min)
    # print('Total: ', (total_time_spend * labor_Price_Min), ' Viagem: ', ((travel_time * travel_Consumption_By_Min) * gas_Price), ' Atividade: ', (activity_time * labor_Gainz_Min))

    cost = ((total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price))

    #print('Gasto Trabalho: ' + str(total_time_spend * labor_Price_Min) + ', Gasto Viagem: ' + str((travel_time * travel_Consumption_By_Min) * gas_Price) + ', Total: ' + str(cost))
    # cost = cost - (activity_time * labor_Gainz_Min)
    # print('Custo: ', cost)
    # print('\n\n\n\n')

    if considerAppointment and appointment:
        cost = cost * values_dict['PRIORITY_APPOINTMENT']
    if considerPriority:
        todayDate = datetime.now().date()
        daysDiference = (todayDate - creationDate).days
        weeksDiference = daysDiference // 7
        mult = values_dict['PRIORITY_CREATION'] ** weeksDiference
        cost = cost * mult


    # print('O que se passou aqui: \n', total_time_spend, ' tempo total x', labor_Price_Min, ' = ',(total_time_spend * labor_Price_Min))
    # print( travel_time, ' tempo viagem x', travel_Consumption_By_Min)
    # print( travel_time * travel_Consumption_By_Min, ' cunsumo viagem x', gas_Price, ' = ', ((travel_time * travel_Consumption_By_Min) * gas_Price))


    return cost


def CostCalculatorBackHome(total_time_spend, travel_time, values_dict):

    # print('Total: ', total_time_spend, ' Viagem: ', travel_time, ' Atividade: ', activity_time)
    travel_Consumption_By_Min = values_dict['GAS_CONSUMPTION']
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60
    # print('gas_Price: ', gas_Price, ' labor_Price_Min: ', labor_Gainz_Min, ' labor_Gainz_Min: ', labor_Price_Min)

    # print('Total: ', (total_time_spend * labor_Price_Min), ' Viagem: ', ((travel_time * travel_Consumption_By_Min) * gas_Price), ' Atividade: ', (activity_time * labor_Gainz_Min))

    # print('tempo total: ', total_time_spend, ' travel time: ', travel_time)
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



def Greedy(worker_Activities_Cluster, workBlock, skills_dict, list_workers, values_dict, considerAppointment, considerPriority, gmaps):


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
    
        # atribuição das vars constantes que vêm do Excel
        travel_Time_By_1KM = values_dict['TRAVEL_TIME']
        tolerance_For_Activity_Post = values_dict['WINDOW_TIME_POST']
        tolerance_For_Activity_Pre = values_dict['WINDOW_TIME_PRE']
        
        # oragnizar a lista da fronteira, copiar o primeiro elemento, o com o menor custo
        frontier = sorted(frontier)
        current_Node = frontier[0]

        # o tempo do node
        current_Time = current_Node.end_Time
        foundActivity = False


        travel_Time_Returning = 0
        for activity in worker_Activities_Cluster:
            
            # como só guardamos o id da tarefa no nó, vamos buscar a última atividade realizada pelo id
            current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

            if not current_Activity:
                current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)
            
            # Tempo necessário para se deslocar até a Atividade
            # travel_Time_Going = Travel_Time(current_Activity.x, current_Activity.y, activity.x, activity.y, gmaps) # type: ignore
            travel_Time_Going = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, activity.x, activity.y) # type: ignore

            # Tempo necessário para se deslocar da Atividade até Casa
            # travel_Time_Returning = Travel_Time( activity.x, activity.y, workBlock.x, workBlock.y, gmaps)
            travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y)

            # Hora de Chegada a Atividade
            datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)

            # verificar se a atividade já foi usada antes neste ramo, basicamente anda para trás a ver as tarefas anteriores, se não estiver lá ele deixa, se estivar lá, não deixa
            if not Belongs_to_Family(current_Node, activity.idActivity):

                # nesta parte verifica os limites do tempo, vai sair daqui
                time_Tolerance_For_Activity_Post = timedelta(minutes=tolerance_For_Activity_Post)
                max_Time_Activity = datetime.combine(datetime.now().date(), activity.appointment) + time_Tolerance_For_Activity_Post


                time_Tolerance_For_Activity_Pre = timedelta(minutes=tolerance_For_Activity_Pre)
                min_Time_Activity = datetime.combine(datetime.now().date(), activity.appointment) - time_Tolerance_For_Activity_Pre
                
                
                # Verificar se consegue chegar a tempo a Atividade
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

                            minutesDayCurrent = activity_End_Time_Real.time().hour * 60 + activity_End_Time_Real.time().minute

                            minutesDayStart = current_Time.time().hour * 60 + current_Time.time().minute

                            # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)

                            # print('\n end time: ', activity_End_Time_Real.time(), ' current time: ', current_Time.time(), ' travel: ', travel_Time_Going)
                            cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, True, activity.creation, values_dict, considerAppointment, considerPriority)
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

                            
                            minutesDayCurrent = activity_End_Time_Real.time().hour * 60 + activity_End_Time_Real.time().minute

                            minutesDayStart = current_Time.time().hour * 60 + current_Time.time().minute

                            #print('Ação demorada')
                            
                            # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                            # print('\n end time: ', activity_End_Time_Real.time(), ' current time: ', current_Time.time(), ' travel: ', travel_Time_Going)

                            cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, True, activity.creation, values_dict, considerAppointment, considerPriority)
                            
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


                        minutesDayCurrent = activity_End_Time_Real.time().hour * 60 + activity_End_Time_Real.time().minute

                        minutesDayStart = current_Time.time().hour * 60 + current_Time.time().minute

                        # print('Brincadeira sem hora limite')
                        
                        # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                        # print('\n end time: ', activity_End_Time_Real.time(), ' current time: ', current_Time.time(), ' travel: ', travel_Time_Going)
                        
                        cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, False, activity.creation, values_dict, considerAppointment, considerPriority)

                        # print('Entrei ATOA: ',activity.idActivity, ', Cost: ', cost)

                        # print('Cost no retorno')
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
            else:
                minutesDayStart = current_Time.time().hour * 60 + current_Time.time().minute
                minutesDayEnd = workBlock.finish.hour * 60 + workBlock.finish.minute

                cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, travel_Time_Returning, values_dict)
                print('\n\n\n\n NÃO CABE MAIS LOGO: COST = ', current_Time.time() , ' - ' , workBlock.finish,'\n\n que é: ', cost)

                # travel_Time_Returning = Travel_Time(current_Activity.x, current_Activity.y, workBlock.x, workBlock.y, gmaps) # type: ignore
                travel_Time_Returning = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, workBlock.x, workBlock.y) # type: ignore
                # print('\n\nCost no Worker-1 foi: ',cost,'\n\n')
                activity_End_Time_Real = datetime_Arraival + timedelta(minutes=time_Required_for_Activity)
                
                
                leaf = Node(workBlock.idWorker, cost, travel_Time_Returning, current_Time + timedelta(minutes=travel_Time_Returning), activity_End_Time_Real, current_Node)
                leaf.state = 0
                heapq.heappush(frontier, leaf)
                frontier.remove(current_Node)
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



