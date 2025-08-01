from queue import PriorityQueue


class State:
    def __init__(self, ships, bases, colonies, time):
        self.ships = ships
        self.bases = bases
        self.colonies = colonies
        self.time = time


def get_input():
    ship = int(input('Number of accessible Starships :'))
    B = int(input('Number of Space Stations on Earth :'))
    C = int(input('Number of Residential Area on Mars :'))
    source = list(map(int, input('Number of Passengers Groups :').split(' ')))
    dest = list(map(int, input('Number of Capacity Residential Area :').split(' ')))
    init_time = list(map(int, input('Number of Time Texas Space Stations :').split(' ')))
    travel_time = list()
    for i in range(B):
        matrix_Time = list(map(int, input('Matrix Time :').split(' ')))
        travel_time.append(matrix_Time)
    return ship, B, C, source, dest, init_time, travel_time

def heuristic(state:State, init_time:list, travel_time):
    h_estimated = []
    for i, g in enumerate(state.bases):
        if g > 0:
            best_travel = min(travel_time[i])
            h_estimated.append(init_time[i] + best_travel)
    if h_estimated:
        max_travel = max(h_estimated)
    else:
        max_travel = 0
    return max_travel

if __name__ == '__main__':
    ship, B, C, source, dest, init_time, travel_time = get_input()
    h = heuristic(B, C, source, dest, init_time, travel_time)
    aStar(ship, B, C, source, dest, init_time, travel_time, h)