from datetime import datetime, time

class Activity:
    activities_quantity = 0

    def __init__(self, id, skill, x, y, creation, appointment = None):
    # def __init__(self, id, Central, codPostal, skill, x, y, appointment = None):
        today = datetime.today()
        self.idActivity = id
        # self.idCentral = Central
        # self.codPostal = codPostal
        self.appointment = appointment if appointment is not None else time(0, 0)
        self.skill = skill
        self.creation = creation
        self.x = x
        self.y = y
        # 0 -> por marcar, 1 -> marcado, 2 -> a ser avaliada
        self.state = 0
        Activity.activities_quantity += 1

    def resetStateToZeroIfNotOne(self):
        if(self.state != 1):
            self.state = 0

    def printActivity(self):
        print('  ID: {}; State: {}; X: {}; Y: {}'.format(self.idActivity, self.state, self.x, self.y))


def Find_Activity_By_Id(list_activities, id):
    for activity in list_activities:
        if(activity.idActivity == id):
            return activity
    return None    # raise ValueError(f"Item com o nome '{id}' não encontrado na lista.")