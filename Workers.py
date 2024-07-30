from datetime import datetime, time
from typing import Optional

from Node import No


class BlocoTrabalho:
     
    def __init__(self, idTrabalhador: str, longitude: float, latitude: float, idBlock: int, inicio: str, fim: str):
        self.idTrabalhador = idTrabalhador
        self.idBloco = idBlock
        self.longitude = longitude
        self.latitude = latitude
        self.listaNos: list[No] = []
        self.inicio = datetime.strptime(inicio.strip(), '%H:%M').time()
        self.fim = datetime.strptime(fim.strip(), '%H:%M').time()

    def atribuir_Nos_Bloco_Trabalho(self, lista_Nos: list[No]):
        self.listaNos = lista_Nos


    def printWorkBlock(self):
        print('    idBlock: {}; Start: {}; Finish: {}'.format( self.idBloco, self.inicio, self.fim))



class Trabalhador:
    quantidade_Trabalhadores = 0

    def __init__(self, id: str, Central: str, competencia: list[str], longitude: float, latitude: float, lista_Blocos_Trabalho: list[BlocoTrabalho]):
        self.idTrabalhador = id
        self.idCentral = Central
        self.competencia = competencia
        self.longitude = longitude
        self.latitude = latitude
        self.quantidadeAtividades = 0
        self.lista_Blocos_Trabalho: list[BlocoTrabalho] = lista_Blocos_Trabalho
        Trabalhador.quantidade_Trabalhadores += 1

    def printWorker(self):
        print('ID: {}; Central: {}; X: {}; Y: {}'.format(self.idTrabalhador, self.idCentral, self.longitude, self.latitude))
        for work_block in self.lista_Blocos_Trabalho:
            work_block.printWorkBlock()

def Find_Worker_By_Id(lista_Trabalhadores: list[Trabalhador], id: str) -> Trabalhador:
    """Encontra o trabalhador com o id fornecido, na lista fornecida

    Args:
        lista_Trabalhadores (list[Trabalhador]): lista com todos os trabalhsdores
        id (str): id fo trabalhador procurado

    Raises:
        ValueError: caso não exista um trabalhador com esse id na lista de trabalhdores

    Returns:
        Worker: o trabalhador encontrado
    """
    for trabalhador in lista_Trabalhadores:
        if(trabalhador.idTrabalhador == id):
            return trabalhador
    raise ValueError(f"ID {id} não encontrado na lista de trabalhadores")