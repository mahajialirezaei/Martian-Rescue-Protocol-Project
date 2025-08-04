import heapq
from typing import List, Tuple, Dict


class State:
    def __init__(self,
                 times: List[float],
                 tasks_done: List[bool],
                 g: float,
                 f: float,
                 previous=None,
                 action=None):
        self.times = times
        self.tasks_done = tasks_done
        self.g = g
        self.f = f
        self.previous = previous
        self.action = action

    def __lt__(self, other):
        return self.f < other.f


def get_input():
    num_ships = int(input())
    num_bases = int(input())
    num_colons = int(input())
    groups = list(map(int, input().split()))
    capacities = list(map(int, input().split()))
    to_base = list(map(int, input().split()))
    travel_matrix = [list(map(int, input().split())) for _ in range(num_bases)]
    return num_ships, num_bases, num_colons, groups, capacities, to_base, travel_matrix


class Scheduler:
    def __init__(self,
                 num_ships: int,
                 base_to_colon: List[Tuple[int, int, float]],
                 texas_to_base: List[float]):

        self.num_ships = num_ships
        self.jobs = base_to_colon
        self.setup = texas_to_base
        self.num_tasks = len(self.jobs)
        self.service_times = [self.setup[base] + t for base, colon, t in self.jobs]

    def heuristic(self, tasks_done: List[bool], times: List[float]) -> float:
        rem = [self.service_times[i] for i, done in enumerate(tasks_done) if done]
        if not rem:
            return 0

        rem.sort(reverse=True)
        est = sorted(times)
        for t in rem:
            index = est.index(min(est))
            est[index] += t

        return max(est) - max(times)


    def search(self) -> State:
        init_times = [0] * self.num_ships
        init_tasks_done = [False] * self.num_tasks
        init_h = self.heuristic(init_tasks_done, init_times)
        init_state = State(times=init_times, tasks_done=init_tasks_done, g = 0, f = init_h)
        search_heap = []
        heapq.heappush(search_heap, init_state)
        watched = {}

        while search_heap:
            pass


    def reconstruct(self, end_state: State) -> List[Tuple[int, int]]:
        path = []
        s = end_state
        while s.previous:
            path.append(s.action)
            s = s.previous
        return list(reversed(path))



if __name__ == '__main__':
    # num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = get_input()
    num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [[6, 7, 8], [10, 9, 2], [6, 3, 7]])
    tasks: List[Tuple[int,int,int]] = []
    for b in range(num_bases):
        for _ in range(base[b]):
            c_best = min(range(num_colons), key=lambda c: travel_matrix[b][c])
            tasks.append((b, c_best, travel_matrix[b][c_best]))
            capacities[c_best] -= 1
    base_to_colon = tasks

    scheduler = Scheduler(num_ships, base_to_colon, to_base)
    end_state = scheduler.search()

    print('Makespan:', end_state.g)
    for ship_idx, task_id in scheduler.reconstruct(end_state):
        base_idx, colon_idx, _ = base_to_colon[task_id]
        print(f"ship_{ship_idx} -> base_{base_idx} -> colon_{colon_idx}")
