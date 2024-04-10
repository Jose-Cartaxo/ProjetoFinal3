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
        family.add(id)
        if parent:
            self.gen = parent.gen + 1
        else:
            self.gen = 0
        if parent:
            self.total_cost = parent.total_cost + cost
        else:
            self.total_cost = 0


    # se for maior tem de retornar true
    def __lt__(self, other):
        if self.gen == 0:
            return True
        if other.gen == 0:
            return False

        return (self.total_cost / self.gen) < (other.total_cost / other.gen)