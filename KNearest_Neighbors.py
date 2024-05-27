from Helper import *
from Workers import *



class KNearest_Nei:
    def __init__(self, atividade, distancia):
        """
        Inicializa a MinhaClasse com um atividade e a distancia ao trabalhador.

       
        Parameters
        ----------
        atividade: (Atividade)
            Atividade que esta a ser ponderada.
        distancia: (Double) 
            distancia em KM entre o local de partida do trabalhador e a atividade.
        """
        self.atividade = atividade
        self.distancia = distancia
    # se for menor tem de retornar true
    def __lt__(self, other):
        return self.distancia < other.distancia


class Coordenada:
    def __init__(self, x, y):
        """
        Inicializa a MinhaClasse com um x e um y, que são as coordenadas.

       
        Parameters
        ----------
        x: (Int)
            coordenada do x.
        y: (Int) 
            coordendada do y.
        """
        self.x = x
        self.y = y


def KNearest_Neighbors_Vote_in(atividade, workblock, skills):
    """
    Esta função verifica se a tarefa deve ser contada para o clustering do workblick ou não, verifica o estado da atividade, verifica o hora de marcação e se possiu as skills necessárias

    Parameters
    ----------
    kNearest_Nei: (KNearest_Nei)
        elemento a comparar com o bloco de trabalho para ver se entra.
    workblock: (WorkBlock)
        workblock que estamos a fazer o clustering das atividades para.
    skills: (list of str)
        lista das skills que o trabalhador possuiu.

    Returns
    -------
    bool
        retorna True ou False, conforme se é para ser adicionada a lista ou não.
    """

    if atividade.appointment != time(0, 0):
  
        if (atividade.state != 1) and (atividade.appointment < workblock.finish) and (atividade.appointment > workblock.start) and (atividade.skill in skills):
            return True
   
    elif (atividade.state != 1) and (atividade.skill in skills):
        return True

    return False



def KNearest_Neighbors1(list_activities, skills, workblock, k):
    """
    Esta função faz o K-NEAREST-NEIGHBORS para o workblock submetido e devolve uma lista com o atividades do cluster

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades existentes.
    list_workers: (list of Worker)
        lista de todos as trabalhadores existentes.
    workblock: (WorkBlock)
        workblock que estamos a fazer o clustering das atividades para.
    k: (Int)
        quantidade de atividades a colocar no Cluster.

    Returns
    -------
    list of Activity
        retorna uma lista das k atividades mais próximas do local de partida do trabalhador.
    """
        
    distances = []
    # worker = Find_Worker_By_Id(list_workers, workblock.idWorker)
    for activity in list_activities:
        distance = Distance_Calculator(activity.x, activity.y, workblock.x, workblock.y)
        distances.append(KNearest_Nei(activity, distance))
    
    print('Fez as distancias todas')
    
    distances = sorted(distances)
    
    list_temp = []
    count = 0
    indi = 0
    while count < k:
        if indi < len(distances):
            if KNearest_Neighbors_Vote_in(distances[indi].atividade, workblock, skills):
                list_temp.append(distances[indi].atividade)
                count += 1
            indi += 1
        else:
            break
    
    print('Já tem a lista')
    return  list_temp



def KNearest_Neighbors2(list_activities, list_workers, workblock, k):
    """
    Esta função faz o clustering das atividades para o workblock.

    Parameters
    ----------
    list_activities: (list of Activity)
        lista de todas as atividades a ponderar para o clustering.
    list_workers: (list of Workers)
        lista de todos os trabalhadores a ponderar para o clustering.
    workblock: (Workblock)
        workblock a ponderar para o clustering.
    k: (Int)
        quantidade de Atividades a colocar no cluster.

    Returns
    -------
    list of Activity
        Retorna uma lista de atividades, que é o cluster final.
    """

    # lista com os Atividades com a respetiva distancia
    distances = []

    # lista com as coordenadas dos elementos que já pertencem ao cluster
    list_coordenada_temp = []

    # lista com os elementes que já pertencem
    list_cluster = []

    # trabalhador que vai realizar este workblock
    worker = Find_Worker_By_Id(list_workers, workblock.idWorker)

    list_coordenada_temp.append(Coordenada(worker.x, worker.y)) # type: ignore
    for count in range(k):

        # colocar as atividades por ordem
        for activity in list_activities:

            # verificar se a atividade ainda não está a ser considerada.
            if activity.state == 0:
                for coord in list_coordenada_temp:
                    distance = Distance_Calculator(activity.x, activity.y, coord.x, coord.y)
                    if KNearest_Neighbors_Vote_in(activity, workblock, worker.skill): # type: ignore
                        distances.append(KNearest_Nei(activity, distance))
        
        distances = sorted(distances)
        if len(distances) != 0:
            atividade_in = distances[0].atividade
            atividade_in.state = 2 
            list_coordenada_temp.append(Coordenada(atividade_in.x, atividade_in.y)) # type: ignore
            list_cluster.append(atividade_in)
            distances.clear()
            
        else:
            return list_cluster
        
    return list_cluster