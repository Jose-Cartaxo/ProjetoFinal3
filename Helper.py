class Stats:
    def __init__(self, idActivity):
        self.ididActivity = idActivity
        self.active = 0
        self.total = 1
    
    def plusOneActive(self):
        self.active = self.active + 1
    
    def plusOne(self):
        self.total = self.total + 1


def DataAnalyticsByHour(listActivities):
    statsList = []
    for activity in listActivities:
        found = False
        for stat in statsList:
            if stat.ididActivity == activity.appointment:
                found = True
                stat.plusOne()
                if activity.state == 1:
                    stat.plusOneActive()
                break
        if not found:
            new = Stats(activity.appointment)
            if activity.state == 1:
                new.plusOneActive()
            statsList.append(new)
    
    return statsList