class Worker:
    workers_quantity = 0

    def __init__(self, id, Central, codPostal, skill, x, y, work_Blocks):
        self.idWorker = id
        self.idCentral = Central
        self.codPostal = codPostal
        self.skill = skill
        self.x = x
        self.y = y
        self.work_Blocks = work_Blocks
        Worker.workers_quantity += 1

    def printWorker(self):
        print('ID: {}; Central: {}; X: {}; Y: {}'.format(self.idWorker, self.idCentral, self.x, self.y))
        for work_block in self.work_Blocks:
            work_block.printWorkBlock()

def Find_Worker_By_Id(list_workers, id):
    for worker in list_workers:
        if(worker.idWorker == id):
            return worker
    raise ValueError(f"Item com o nome ",id," não encontrado na lista.")

class WorkBlock:
     
    def __init__(self, idWorker, idBlock, start, finish):
        self.idWorker = idWorker
        self.idBlock = idBlock
        self.start = start
        self.finish = finish
        self.block_List = []

    def printWorkBlock(self):
        print('    idBlock: {}; Start: {}; Finish: {}'.format( self.idBlock, self.start, self.finish))


from datetime import datetime, time
class ActivityBlock:

    def __init__(self, idActivity, start, finish):
        self.idActivity = idActivity
        self.start = start
        self.finish = finish
        
    def printActivityBlock(self):
        print('idWorker: {}; idBlock: {}; Start: {}; Finish: {}'.format(self.idActivity, self.start, self.finish))


def Create_List_Work_Blocks():
        
    today = datetime.today()
    
    # Horario Manhã
    time_start_morning = datetime.combine(today, time(8, 0, 0))
    time_end_morning = datetime.combine(today, time(12, 0, 0))

    # Defina os horários da tarde
    time_start_afternoon = datetime.combine(today, time(13, 0, 0))
    time_end_afternoon = datetime.combine(today, time(17, 0, 0))


    work_block_morning = WorkBlock( '62764df6-b097-42b1-aa9c-65bf1c48ebc5', 1, time_start_morning, time_end_morning)
    work_block_aftermoon = WorkBlock( '62764df6-b097-42b1-aa9c-65bf1c48ebc5', 2, time_start_afternoon, time_end_afternoon)

    return  [work_block_morning, work_block_aftermoon]