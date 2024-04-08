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

class WorkBlock:
     
    def __init__(self, idWorker, idBlock, start, finish):
        self.idWorker = idWorker
        self.idBlock = idBlock
        self.start = start
        self.finish = finish
        self.block_List = []

    def printWorkBlock(self):
        print('    idBlock: {}; Start: {}; Finish: {}'.format( self.idBlock, self.start, self.finish))

class ActivityBlock:

    def __init__(self, idActivity, start, finish):
        self.idActivity = idActivity
        self.start = start
        self.finish = finish
        
    def printActivityBlock(self):
        print('idWorker: {}; idBlock: {}; Start: {}; Finish: {}'.format(self.idActivity, self.start, self.finish))