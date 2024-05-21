import heapq

from bson import _get_decimal128
from Activity import Find_Activity_By_Id
from Node import Node
from Workers import Worker
from Workers import Find_Worker_By_Id
from DBSCANS import Travel_Time
from datetime import datetime, timedelta, time
import pandas as pd

def CostCalculator(total_time_spend, travel_time, appointment, creationDate, values_dict, considerAppointment, considerPriority):
    """
    Esta função calcula o custo, tem em conta se o utilizador pretende dar prioridade às atividade mais antigas ou às atividades com agendamento a cumprir ou não.

    Parameters
    ----------
    total_time_spend: (int)
        quantidade de tempo em minutos gasta.
    travel_time: (float)
        quantidade de tempo em minutos gasta em viagem.
    appointment: (bool)
        se tem agendamento ou não.
    creationDate: (datetime.date)
        data de criação da atividade pode ser usadao caso o utilizador queira dar prioridade as atividades agendadas a mais tempo
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
    considerAppointment: (bool)
        bool que se for true significa que o utilizador quer considerar as atividades com agendamento mais prioritárias do que as sem, false são todas iguais
    considerPriority: (bool)
        bool que se for true significa que o utilizador quer considerar as atividades com agendamento mais antigo mais prioritárias do que as com mais recente, false são todas iguais

        
    Returns
    -------
    int
        Retorna o custo da viagem até a atividade.
    """

    travel_Consumption_By_Min = values_dict['GAS_CONSUMPTION'] # 
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60

    cost = ((total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price))

    if considerAppointment and appointment:
        cost = cost * values_dict['PRIORITY_APPOINTMENT']
    if considerPriority:
        todayDate = datetime.now().date()
        daysDiference = (todayDate - creationDate).days
        weeksDiference = daysDiference // 7
        mult = values_dict['PRIORITY_CREATION'] ** weeksDiference
        cost = cost * mult


    return cost


def CostCalculatorBackHome(total_time_spend, travel_time, values_dict):

    """
    Esta função calcula o custo de viagem de volta a casa.

    Parameters
    ----------
    total_time_spend: (int)
        quantidade de tempo em minutos gasta.
    travel_time: (float)
        quantidade de tempo em minutos gasta em viagem.
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        
    Returns
    -------
    Int
        Retorna o custo da viagem de volta a casa.
    """


    travel_Consumption_By_Min = values_dict['GAS_CONSUMPTION']
    gas_Price = values_dict['GAS_PRICE']
    labor_Price_Hr = values_dict['LABOR_PRICE']
    labor_Price_Min = labor_Price_Hr / 60


    cost = (total_time_spend * labor_Price_Min) + ((travel_time * travel_Consumption_By_Min) * gas_Price)

    return cost


def adicionarMinutosADatetimeTime(tim, min):

    minutosTotais = tim.minute + min

    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = minutosTotais // 60
    minutos = minutosTotais % 60

    horas = tim.hour + quantidadeDeHoras 
    horas = horas % 24

    return time(horas, minutos)

def subtrairMinutosADatetimeTime(tim, min):
    # quantidade de horas dentro dos minutos
    quantidadeDeHoras = min // 60
    min = min % 60
    
    horas = tim.hour - quantidadeDeHoras
    
    if min > tim.minute:
        horas = horas - 1
        min = 60 - (min - tim.minute)
    else: 
        min = tim.minute - min 

    horas = horas % 24
    if horas < 0:
        horas = horas + 24
    
    saida = time(horas, min)
    return saida


def Greedy(worker_Activities_Cluster, workBlock, skills_dict, list_workers, values_dict, considerAppointment, considerPriority, gmaps):

    """
    Esta função verifica qual a melhor combinação de atividades para o trabalhador, faz lhe a rota e devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades.

    Parameters
    ----------
    worker_Activities_Cluster: (list of Activity.Activity)
        quantidade de tempo em minutos gasta.
    workBlock: (Workers.WorkBlock)
        quantidade de tempo em minutos gasta em viagem.
    skills_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    list_workers: (list of Workers.Worker)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    values_dict: (dict)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    considerAppointment: (bool)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    considerPriority: (bool)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        quantidade de tempo em minutos gasta em viagem.
    gmaps: (googlemaps.client.Client)
        dicionário com os valores importados do Excel para ser utilizados nos calculos
        
    Returns
    -------
    list of Node
        devolve uma lista nós, pela ordem pela qual devem ser percorridas as atividades
    """

    # Aqui cria uma lista "frontier", para guardar os nós que estão na fronteira
    frontier = []
    
    # current_DateTime = datetime.now()
    # time_starting = datetime.combine(current_DateTime.date(), workBlock.start)

    # atribuição das vars constantes que vêm do dicionário, que veio do Excel
    travel_Time_By_1KM = values_dict['TRAVEL_TIME']
    tolerance_For_Activity_Post = int (values_dict['WINDOW_TIME_POST'])
    tolerance_For_Activity_Pre = int (values_dict['WINDOW_TIME_PRE'])

    # inicio é o WorkBlock
    frontier.append(Node(workBlock.idWorker, 0, 0,workBlock.start, workBlock.start, None))

    # enquanto existirem elementos na lista "frontier", ou então quando um ramo finalizado voltar a ser escolhido ele dá o gosht

    while frontier:

        # organizar a lista da fronteira, copiar o primeiro elemento (o com o menor custo)
        frontier = sorted(frontier)
        current_Node = frontier[0]

        '''
        print('\n\n\n')
        for nozinho in frontier:
            nozinho.printNodeGen()
            print('\n')
        print('\n\n\n')
        '''

        # a hora em que o node atual acabou, a hora a partir da qual vamos começar
        current_Time = current_Node.end_Time

        # se encontrar atividade passa a true, isto para ser usado mais a frente, pois se não conseguir encontrar mais atividades, volta para casa
        foundActivity = False

        # aqui percorre todas as atividades do cluster, isto para as tentar adicionar a rota
        for activity in worker_Activities_Cluster:
            
            # aqui temos um problema pois se no futuro se for possivel um trabalhador e uma atividade terem o mesmo id, isto começa a dar raia
            # como só guardamos o id da tarefa no nó, vamos buscar a última atividade realizada pelo id
            current_Activity = Find_Activity_By_Id(worker_Activities_Cluster,current_Node.id)

            # se não existir uma atividade com o id é por que é porque é um trabalhador, por exemplo o primeiro nó da lista
            if not current_Activity:
                current_Activity = Find_Worker_By_Id(list_workers, current_Node.id)
            
            # Tempo necessário para se deslocar até a Atividade
            travel_Time_Going = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, activity.x, activity.y, gmaps) # type: ignore

            # Tempo necessário para se deslocar da Atividade até Casa
            travel_Time_Returning = Travel_Time(travel_Time_By_1KM, activity.x, activity.y, workBlock.x, workBlock.y, gmaps)

            # Hora de Chegada a Atividade
            datetime_Arraival = adicionarMinutosADatetimeTime(current_Time, travel_Time_Going)
            # datetime_Arraival = current_Time + timedelta(minutes=travel_Time_Going)

            # verificar se a atividade já foi usada antes neste ramo, basicamente anda para trás a ver as tarefas anteriores, se não estiver lá ele deixa, se estivar lá, não deixa
            if not activity.idActivity in current_Node.family :


                max_Time_Activity = adicionarMinutosADatetimeTime(activity.appointment, tolerance_For_Activity_Post)


                min_Time_Activity = subtrairMinutosADatetimeTime(activity.appointment, tolerance_For_Activity_Pre)
                
                # as atividades com o tempod e agendamento == 00:00 não têm de cumprir o agendamento, ou seja podem ser realizadas a qualquer hora.

                # Então verifica se é deste tipo, se não for continua, se for, tem de ir a volta
                if not activity.appointment == time(0, 0):

                    # Verificar se consegue chegar a tempo a Atividade
                    if datetime_Arraival < max_Time_Activity:
                        # print('Passou')

                        
                        # Ele aqui, se sair da Atividade anterior e vier diretamente para a atual está dentro do espaço de tempo de tolerância, ou seja, pode vir e começar a Trabalhar emidiatamente, sem tempos de espera para o inicio
                        if datetime_Arraival > min_Time_Activity:
                            

                            # Tempo necessário para a Atividade em si
                            time_Required_for_Activity = skills_dict[activity.skill]
                            # print('tempo para realizar a tarefa: ', time_Required_for_Activity)


                            # Tempo necessário para chegar a Casa
                            time_Required = time_Required_for_Activity + travel_Time_Returning
                            # print('tempo total: ', time_Required)
                            

                            # Tempo em que acaba a Tarefa
                            activity_End_Time_Real =  adicionarMinutosADatetimeTime(datetime_Arraival, time_Required_for_Activity)


                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            activity_End_Time_Home = adicionarMinutosADatetimeTime(datetime_Arraival, time_Required)

                            if activity_End_Time_Home < workBlock.finish:
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

                                minutesDayCurrent = activity_End_Time_Real.hour * 60 + activity_End_Time_Real.minute

                                minutesDayStart = current_Time.hour * 60 + current_Time.minute

                                cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, True, activity.creation, values_dict, considerAppointment, considerPriority)
                                

                                frontier.append(Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real, current_Node))

                                


                        else:
                            # Tempo necessário para a Atividade em si
                            time_Required_for_Activity = skills_dict[activity.skill]

                            # Tempo necessário para chegar a Casa
                            time_Required = time_Required_for_Activity + travel_Time_Returning
                            
                            # Tempo em que acaba a Tarefa
                            activity_End_Time_Real = adicionarMinutosADatetimeTime(min_Time_Activity, time_Required_for_Activity)

                            # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                            activity_End_Time_Home = adicionarMinutosADatetimeTime(min_Time_Activity, time_Required)


                            if activity_End_Time_Home < workBlock.finish:
                                foundActivity = True

                                
                                minutesDayCurrent = activity_End_Time_Real.hour * 60 + activity_End_Time_Real.minute

                                minutesDayStart = current_Time.hour * 60 + current_Time.minute

                                #print('Ação demorada')
                                
                                # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                                # print('\n end time: ', activity_End_Time_Real.time(), ' current time: ', current_Time.time(), ' travel: ', travel_Time_Going)

                                cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, True, activity.creation, values_dict, considerAppointment, considerPriority)
                                
                                # print('Entrei a meio da Atividade: ',activity.idActivity, ', Cost: ', cost)
                                
                                frontier.append(Node(activity.idActivity, cost, travel_Time_Going, min_Time_Activity, activity_End_Time_Real , current_Node))



                else:
                    # Tempo necessário para a Atividade em si
                    time_Required_for_Activity = skills_dict[activity.skill]

                    # Tempo necessário para chegar a Casa
                    time_Required = time_Required_for_Activity + travel_Time_Returning
                    
                    # Tempo em que acaba a Tarefa
                    activity_End_Time_Real = adicionarMinutosADatetimeTime( datetime_Arraival, time_Required_for_Activity)

                    # Verificar se tem Tempo para voltar a casa, se não olha, já não cabe
                    activity_End_Time_Home = adicionarMinutosADatetimeTime( datetime_Arraival, time_Required)

                    if activity_End_Time_Home < workBlock.finish:
                        foundActivity = True


                        minutesDayCurrent = activity_End_Time_Real.hour * 60 + activity_End_Time_Real.minute

                        minutesDayStart = current_Time.hour * 60 + current_Time.minute

                        # print('Brincadeira sem hora limite')
                        
                        # print('minutesDayCurrent', minutesDayStart - minutesDayCurrent, ', travel_Time_Going:', travel_Time_Going, ', time_Required_for_Activity:', time_Required_for_Activity)
                        # print('\n end time: ', activity_End_Time_Real.time(), ' current time: ', current_Time.time(), ' travel: ', travel_Time_Going)
                        
                        cost = CostCalculator(minutesDayCurrent - minutesDayStart, travel_Time_Going, False, activity.creation, values_dict, considerAppointment, considerPriority)

                        # print('Entrei ATOA: ',activity.idActivity, ', Cost: ', cost)

                        # print('Cost no retorno')
                        frontier.append(Node(activity.idActivity, cost, travel_Time_Going, datetime_Arraival, activity_End_Time_Real , current_Node))



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
                minutesDayStart = current_Time.hour * 60 + current_Time.minute
                minutesDayEnd = workBlock.finish.hour * 60 + workBlock.finish.minute

                cost = CostCalculatorBackHome(minutesDayEnd - minutesDayStart, travel_Time_Returning, values_dict)
                # print('\n\n\n\n NÃO CABE MAIS LOGO: COST = ', current_Time.time() , ' - ' , workBlock.finish,'\n\n que é: ', cost)

                # travel_Time_Returning = Travel_Time(current_Activity.x, current_Activity.y, workBlock.x, workBlock.y, gmaps) # type: ignore
                travel_Time_Returning = Travel_Time(travel_Time_By_1KM, current_Activity.x, current_Activity.y, workBlock.x, workBlock.y, gmaps) # type: ignore
                # print('\n\nCost no Worker-1 foi: ',cost,'\n\n')
                
                time_Required_for_Activity = skills_dict[activity.skill]
                
                activity_End_Time_Real = adicionarMinutosADatetimeTime( datetime_Arraival, time_Required_for_Activity)
                
                
                leaf = Node(workBlock.idWorker, cost, travel_Time_Returning, adicionarMinutosADatetimeTime( current_Time, travel_Time_Returning), activity_End_Time_Real, current_Node)
                leaf.state = 0
                frontier.append(leaf)
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



