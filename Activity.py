from datetime import time, date

class Atividade:
    
    activities_quantity = 0

    def __init__(self, id: str, Central: str, competencia: str, longitude: float, latitude: float, data_criacao: date, agendamento = None):
        self.idAtividade: str = id
        self.idCentral: str = Central
        self.competencia: str = competencia
        self.longitude: float = longitude
        self.latitude: float = latitude
        self.data_criacao: date = data_criacao
        self.agendamento: time = agendamento if agendamento is not None else time(0, 0)
        # 0 -> por marcar, 1 -> marcado, 2 -> a ser avaliada
        self.estado = 0
        Atividade.activities_quantity += 1

    def estado_A_0_Se_Diferente_De_1(self):
        """Altera o estado da atividade para 0 caso seja diferente de 1
        """
        if(self.estado != 1):
            self.estado = 0

    def print_Atividade(self):
        """Faz um print com informação da atividade (id, estado, x e y)
        """
        print('  ID: {}; Estado: {}; X: {}; Y: {}'.format(self.idAtividade, self.estado, self.longitude, self.latitude))


def Encontrar_Atividade_Por_Id(lista_atividades: list[Atividade], id: str) -> Atividade | None:
    """_Devolve a Atividade na lista fornecida, através do id, se não encontrar devolve Node_ 

    Args:
        list_activities (list[Activity]): _Lista de atividades onde se está a procurar_
        id (str): _Id da Atividade que se pretende encontrar_

    Returns:
        Activity: a atividade procurada
    """
    for atividade in lista_atividades:
        if(atividade.idAtividade == id):
            return atividade
    return None # raise ValueError(f"Item com o nome '{id}' não encontrado na lista.")