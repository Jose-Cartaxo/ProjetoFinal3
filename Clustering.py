import math

from numpy import double
from Activity import *


def Distance_Calculator( x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def KNearest_Neighbors(activities, x, y, k):
    distances = []
    for activity in activities:
        distancia = Distance_Calculator(activity.x, activity.y, x, y)
        distances.append((distancia, activity))

    distances = sorted(distances, key=lambda x: x[0])
    return distances[:k]

