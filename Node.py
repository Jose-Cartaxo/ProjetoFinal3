class Node:
    def __init__(self, id_Activity, cost, end_Time, family, parent):
        self.id_Activity = id_Activity
        self.cost = cost
        self.end_Time = end_Time
        self.family = family.copy()
        self.parent = parent
        family.add(family)
        self.gen = parent.gen + 1
        self.total_cost = parent.total_cost + cost


    def __lt__(self, other):
        return (self.total_cost / self.gen) < (other.total_cost / other.gen)