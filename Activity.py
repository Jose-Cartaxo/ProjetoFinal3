class Activity:
    activities_quantity = 0

    def __init__(self, id, Central, codPostal, skill, x, y, appointment = None):
        self.idActivity = id
        self.idCentral = Central
        self.codPostal = codPostal
        self.appointment = appointment if appointment is not None else -1
        self.skill = skill
        self.x = x
        self.y = y
        # 0 -> por marcar, 1 -> marcado, 2 -> a ser avaliada
        self.state = 0
        Activity.activities_quantity += 1

    
    def printActivity(self):
        print('ID: {}; Central: {}; X: {}; Y: {}'.format(self.idActivity, self.idCentral, self.x, self.y))

