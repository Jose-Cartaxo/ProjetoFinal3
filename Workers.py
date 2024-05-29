from datetime import datetime, time
from typing import Optional

class Worker:
    workers_quantity = 0

    def __init__(self, id, Central, competencia, longitude, latitude, work_Blocks):
        self.idWorker = id
        self.idCentral = Central
        self.competencia = competencia
        self.longitude = longitude
        self.latitude = latitude
        self.work_Blocks = work_Blocks
        Worker.workers_quantity += 1

    def printWorker(self):
        print('ID: {}; Central: {}; X: {}; Y: {}'.format(self.idWorker, self.idCentral, self.longitude, self.latitude))
        for work_block in self.work_Blocks:
            work_block.printWorkBlock()

def Find_Worker_By_Id(list_workers, id) -> Worker:
    for worker in list_workers:
        if(worker.idWorker == id):
            return worker
    raise ValueError(f"ID {id} não encontrado na lista de trabalhadores")

class WorkBlock:
     
    def __init__(self, idWorker: str, longitude: float, latitude: float, idBlock: int, inicio: str, fim: str):
        self.idWorker = idWorker
        self.idBlock = idBlock
        self.longitude = longitude
        self.latitude = latitude
        self.inicio = datetime.strptime(inicio.strip(), '%H:%M').time()
        self.fim = datetime.strptime(fim.strip(), '%H:%M').time()

    def printWorkBlock(self):
        print('    idBlock: {}; Start: {}; Finish: {}'.format( self.idBlock, self.inicio, self.fim))



'''

class ActivityBlock:

    def __init__(self, idActivity, start, finish):
        self.idActivity = idActivity
        self.start = start
        self.finish = finish
        
    def printActivityBlock(self):
        print('idWorker: {}; idBlock: {}; Start: {}; Finish: {}'.format(self.idActivity, self.start, self.finish))

'''