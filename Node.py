from re import X


class Node:
    def __init__(self, id, cost, travel_Time, start_Time, end_Time, parent):
        self.id = id
        self.cost = cost
        self.travel_Time = travel_Time
        self.start_Time = start_Time
        self.end_Time = end_Time
        self.parent = parent

        if parent:
            self.gen = parent.gen + 1
            self.total_cost = parent.total_cost + cost
            self.family = parent.family.copy()
        else:
            self.gen = 0
            self.total_cost = 0
            self.family = []
            self.family.append(id)
        

    def printNode(self):
        print('ID: ', self.id, ' Cost: ', self.total_cost, ' end_Time: ', self.end_Time, ' Gen: ', self.gen)

    # se for maior tem de retornar true
    def __lt__(self, other):
        if self.gen == 0:
            return False
        if other.gen == 0:
            return True
        
        # return self.total_cost < other.total_cost 
        return (self.total_cost / self.gen) < (other.total_cost / other.gen)