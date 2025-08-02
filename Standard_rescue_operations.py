from queue import PriorityQueue

from numpy.ma.core import negative


class State:
    def __init__(self, ships, bases, colonies, time):
        self.ships = tuple(ships)
        self.bases = tuple(bases)
        self.colonies = tuple(colonies)
        self.time = time

    def __eq__(self, other):
        return (self.ships, self.bases, self.colonies, self.time) == \
               (other.ships, other.bases, other.colonies, other.time)

    def __hash__(self):
        return hash((self.ships, self.bases, self.colonies, self.time))

    def __repr__(self):
        return f"S(time={self.time}, bases={self.bases}, cols={self.colonies})"


def get_input():
    ship = int(input('Number of accessible Starships :'))
    B = int(input('Number of Space Stations on Earth :'))
    C = int(input('Number of Residential Area on Mars :'))
    bases = list(map(int, input('Number of Passengers Groups :').split(' ')))
    colonies = list(map(int, input('Number of Capacity Residential Area :').split(' ')))
    init_time = list(map(int, input('Number of Time Texas Space Stations :').split(' ')))
    travel_time = list()
    for i in range(B):
        matrix_Time = list(map(int, input('Matrix Time :').split(' ')))
        travel_time.append(matrix_Time)
    return ship, B, C, bases, colonies, init_time, travel_time

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


def apply_action(state:State, action, init_time, travel_time):
    ship_index, base_index, colon_index = action
    depart = max(state.time, state.ships[ship_index][1])
    cost = init_time[ship_index] + travel_time[ship_index]
    arrive_to_dest = depart + cost

    new_ships = list(state.ships)
    new_bases = list(state.bases)
    new_colonies = list(state.colonies)
    new_ships[ship_index] = ('col' + str(colon_index), arrive_to_dest)
    new_bases[base_index] -= 1
    new_colonies[colon_index] -= 1

    new_state = State(new_ships, new_bases, new_colonies, arrive_to_dest)
    return new_state


def aStar(ship, B, C, bases, colonies, init_time, travel_time):
    start_ships = [('idle', 0) for x in range(ship)]
    start = State(start_ships, bases=bases, colonies=colonies, time=0)


    pq = PriorityQueue()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, init_time, travel_time)}

    pq.put((f_score[start], start))
    while not pq.empty():
        current_f, current = pq.get()
        if sum(current.states) == 0:
            return reconstruct_travel_path(came_from, current)

        possible_acts = possible_actions(current, init_time, travel_time)
        for action in possible_acts:
            neigbor = apply_action(current, action, init_time, travel_time)


            if neigbor not in g_score or neigbor.time < g_score[neigbor]:
                came_from[neigbor] = (current, action)
                g_score[neigbor] = neigbor.time
                f_score[neigbor] = heuristic(neigbor, init_time, travel_time) + g_score[neigbor]
                pq.put((f_score[neigbor], neigbor))
    return None

def reconstruct_travel_path(came_from, current):
    travel_path = []
    while current in came_from:
        prev, action = came_from[current]
        travel_path.append(action)
        current = prev
    travel_path = list(reversed(travel_path))
    return travel_path




def possible_actions(state:State, init_time, travel_time):
    actions = []
    for ship_index, (loc, av) in enumerate(state.ships):
        if av <= state.time:
            for base_index, group in enumerate(state.bases[ship_index]):
                if group > 0:
                    for colon_index, capacity in enumerate(state.colonies[ship_index]):
                        if capacity > 0:
                            actions.append((ship_index, base_index, colon_index))

    return actions

if __name__ == '__main__':
    ship, B, C, bases, colonies, init_time, travel_time = get_input()
    aStar(ship, B, C, bases, colonies, init_time, travel_time)
