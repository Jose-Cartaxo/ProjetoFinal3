from re import X


class Node:
    def __init__(self, id, cost, x, y, end_Time, family, parent):
        self.id = id
        self.cost = cost
        self.x = x 
        self.y = y
        self.end_Time = end_Time
        self.family = family.copy()
        self.parent = parent
        family.append(id)
        if parent:
            self.gen = parent.gen + 1
        else:
            self.gen = 0
        if parent:
            self.total_cost = parent.total_cost + cost
        else:
            self.total_cost = 0

    def printNode(self):
        print('ID: ', self.id, ' Cost: ', self.total_cost, ' Gen: ', self.gen)

    # se for maior tem de retornar true
    def __lt__(self, other):
        if self.gen == 0:
            return False
        if other.gen == 0:
            return True

        return (self.total_cost / self.gen) < (other.total_cost / other.gen)