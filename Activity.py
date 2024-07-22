from datetime import time, date

class Activity:
    
    activities_quantity = 0

    def __init__(self, id: str, Central: str, competencia: str, longitude: float, latitude: float, data_criacao: date, agendamento = None):
        self.idActivity = id
        self.idCentral = Central
        self.agendamento = agendamento if agendamento is not None else time(0, 0)
        self.competencia = competencia
        self.data_criacao = data_criacao
        self.longitude = longitude
        self.latitude = latitude
        # 0 -> por marcar, 1 -> marcado, 2 -> a ser avaliada
        self.state = 0
        Activity.activities_quantity += 1

    def resetStateToZeroIfNotOne(self):
        if(self.state != 1):
            self.state = 0

    def printActivity(self):
        print('  ID: {}; State: {}; X: {}; Y: {}'.format(self.idActivity, self.state, self.longitude, self.latitude))


def Find_Activity_By_Id(list_activities: list[Activity], id: str) -> Activity | None:
    """_Devolve a Atividade na lista fornecida, através do id, se não encontrar devolve Node_ 

    Args:
        list_activities (list[Activity]): _Lista de atividades onde se está a procurar_
        id (str): _Id da Atividade que se pretende encontrar_

    Returns:
        Activity: a atividade procurada
    """
    for activity in list_activities:
        if(activity.idActivity == id):
            return activity
    return None # raise ValueError(f"Item com o nome '{id}' não encontrado na lista.")