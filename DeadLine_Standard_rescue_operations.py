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

    def __str__(self):
        return str(self.times) + str(self.tasks_done) + str(self.g) + str(self.f) + str(self.previous) + '\n'


def get_input():
    num_ships = int(input())
    num_bases = int(input())
    num_colons = int(input())
    groups = list(map(int, input().split()))
    capacities = list(map(int, input().split()))
    to_base = list(map(int, input().split()))
    deadLine = list(map(int, input().split()))
    travel_matrix = [list(map(int, input().split())) for _ in range(num_bases)]
    return num_ships, num_bases, num_colons, groups, capacities, to_base, deadLine, travel_matrix


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
        rem = [self.service_times[i] for i, done in enumerate(tasks_done) if not done]
        if not rem:
            return 0

        rem.sort(reverse=True)
        est = sorted(times)
        for t in rem:
            index = est.index(min(est))
            est[index] += t

        return max(est) - max(times)


    def search(self):
        init_times = [0] * self.num_ships
        init_tasks_done = [False] * self.num_tasks
        init_h = self.heuristic(init_tasks_done, init_times)
        init_state = State(times=init_times, tasks_done=init_tasks_done, g = 0, f = init_h)
        search_heap = []
        heapq.heappush(search_heap, init_state)
        watched = {}

        while search_heap:
            cur = heapq.heappop(search_heap)
            if all(cur.tasks_done):
                return cur
            key = (tuple(cur.tasks_done), tuple(cur.times))
            if key in watched.keys() and watched[key] < cur.g:
                continue
            watched[key] = cur.g

            for tsk_id in range(self.num_tasks):
                if cur.tasks_done[tsk_id]:
                    continue
                base, colon, t = self.jobs[tsk_id]
                service = self.setup[base] + t
                for sh in range(self.num_ships):
                    new_time = cur.times.copy()
                    new_time[sh] += service
                    new_tasks_done = cur.tasks_done.copy()
                    new_tasks_done[tsk_id] = True
                    new_g = max(cur.g, new_time[sh])
                    h = self.heuristic(new_tasks_done, new_time)
                    new_state = State(new_time, new_tasks_done, new_g, new_g + h, previous=cur, action=(sh, tsk_id))
                    heapq.heappush(search_heap, new_state)

    def reconstruct(self, end_state: State) -> List[State]:
        path = []
        s = end_state
        while s.previous:
            path.append(s.action)
            s = s.previous
        return list(reversed(path))

    def print_schedule_with_stages(self, end_state: State):
        schedule = self.reconstruct(end_state)
        base_to_colon = self.jobs
        texas_to_base = self.setup
        num_ships = self.num_ships

        current_times = [0.0] * num_ships
        detailed = []
        for step, (ship_idx, task_id) in enumerate(schedule):
            base_idx, colon_idx, travel = base_to_colon[task_id]
            service = texas_to_base[base_idx] + travel
            start = current_times[ship_idx]
            end = start + service
            current_times[ship_idx] = end
            detailed.append((ship_idx, task_id, base_idx, colon_idx, service, start, end))

        detailed.sort(key= lambda x:x[5])
        for step, detail in enumerate(detailed):
            ship_idx, task_id, base_idx, colon_idx, service, start, end = detail
            print(f"step: {step}, ship_idx: {ship_idx}, base_idx: {base_idx}, colon_idx: {colon_idx}, start: {start}, end: {end}")


if __name__ == '__main__':
    # num_ships, num_bases, num_colons, base, capacities, to_base, deadLine, travel_matrix = get_input()
    num_ships, num_bases, num_colons, base, capacities, to_base, deadLine, travel_matrix = (3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [-1, -1, 10], [[6, 7, 8], [10, 9, 2], [6, 3, 7]])
    tasks: List[Tuple[int,int,int]] = []
    for b in range(num_bases):
        for _ in range(base[b]):
            best_colon = min(range(num_colons), key=lambda c: travel_matrix[b][c])
            tasks.append((b, best_colon, travel_matrix[b][best_colon]))
            capacities[best_colon] -= 1
    base_to_colon = tasks

    scheduler = Scheduler(num_ships, base_to_colon, to_base)
    end_state = scheduler.search()

    print('endTime:', end_state.g)
    scheduler.print_schedule_with_stages(end_state)