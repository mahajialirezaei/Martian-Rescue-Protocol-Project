import heapq
from typing import List, Tuple, Dict

class State:
    def __init__(self,
                 times: List[float],
                 tasks_done: List[bool],
                 g: float,
                 f: float,
                 ship_previous_colons: List[int] = None,
                 previous=None,
                 action=None):
        self.times = times
        self.tasks_done = tasks_done
        self.g = g
        self.f = f
        if ship_previous_colons is None:
            self.ship_previous_colons = [-1] * len(times)
        else:
            self.ship_previous_colons = ship_previous_colons
        self.previous = previous
        self.action = action

    def __lt__(self, other):
        return self.f < other.f

    def __str__(self):
        return (str(self.times) + '\n'
                + str(self.tasks_done) + '\n' + str(self.g) + str(self.f) + '\n' +
                str(self.ship_previous_colons) + '\n' + str(self.previous) + '\n')

class Scheduler:
    def __init__(self,
                 num_ships: int,
                 base_to_colon: List[Tuple[int, int, float]],
                 texas_to_base: List[float],
                 matrix_time: List[List[int]]):
        self.num_ships = num_ships
        self.jobs = base_to_colon
        self.setup = texas_to_base
        self.num_tasks = len(self.jobs)
        self.matrix_time = matrix_time

        # lower-bound service for each job (admissible heuristic component):
        # min possible for a job = min(setup[base], min(matrix_time[base])) + travel
        self.min_service = []
        for (b, c, travel) in self.jobs:
            min_return = min(self.matrix_time[b])  # min travel from base b to any colon (as prev)
            self.min_service.append(min(self.setup[b], min_return) + travel)

    def heuristic(self, tasks_done: List[bool], times: List[float]) -> float:
        rem = [self.min_service[i] for i, done in enumerate(tasks_done) if not done]
        if not rem:
            return 0.0
        rem.sort(reverse=True)
        est = sorted(times)
        for t in rem:
            est[0] += t
            est.sort()
        return max(est) - max(times)

    def search(self):
        init_times = [0.0] * self.num_ships
        init_tasks_done = [False] * self.num_tasks
        init_ship_prev = [-1] * self.num_ships
        init_h = self.heuristic(init_tasks_done, init_times)
        init_state = State(times=init_times, tasks_done=init_tasks_done, g=0.0, f=init_h,
                           ship_previous_colons=init_ship_prev)
        search_heap = []
        heapq.heappush(search_heap, init_state)
        watched = {}

        while search_heap:
            cur = heapq.heappop(search_heap)
            if all(cur.tasks_done):
                return cur
            key = (tuple(cur.tasks_done), tuple(cur.times), tuple(cur.ship_previous_colons))
            # use <= to prune equal-or-worse states (optional)
            if key in watched and watched[key] <= cur.g:
                continue
            watched[key] = cur.g

            for tsk_id in range(self.num_tasks):
                if cur.tasks_done[tsk_id]:
                    continue
                base, colon, travel = self.jobs[tsk_id]
                for sh in range(self.num_ships):
                    new_time = cur.times.copy()
                    new_tasks_done = cur.tasks_done.copy()
                    new_tasks_done[tsk_id] = True
                    new_prev = cur.ship_previous_colons.copy()
                    prev_colon = new_prev[sh]
                    if prev_colon == -1:
                        added = self.setup[base] + travel
                    else:
                        # return from previous colon then go to new colon (rule you specified)
                        added = self.matrix_time[base][prev_colon] + travel

                    new_time[sh] += added
                    new_prev[sh] = colon
                    new_g = max(cur.g, new_time[sh])
                    h = self.heuristic(new_tasks_done, new_time)
                    new_state = State(new_time, new_tasks_done, new_g, new_g + h,
                                      ship_previous_colons=new_prev,
                                      previous=cur, action=(sh, tsk_id))
                    heapq.heappush(search_heap, new_state)

        return None

    def reconstruct(self, end_state: State) -> List[Tuple[int, int]]:
        path = []
        s = end_state
        while s.previous is not None:
            path.append(s.action)
            s = s.previous
        return list(reversed(path))

    def print_schedule_with_stages(self, end_state: State):
        schedule = self.reconstruct(end_state)
        base_to_colon = self.jobs
        current_times = [0.0] * self.num_ships
        prev_col = [-1] * self.num_ships
        detailed = []

        for step, (ship_idx, task_id) in enumerate(schedule):
            base_idx, colon_idx, travel = base_to_colon[task_id]
            if prev_col[ship_idx] == -1:
                service = self.setup[base_idx] + travel
            else:
                service = self.matrix_time[base_idx][prev_col[ship_idx]] + travel
            start = current_times[ship_idx]
            end = start + service
            current_times[ship_idx] = end
            prev_col[ship_idx] = colon_idx
            detailed.append((ship_idx, task_id, base_idx, colon_idx, service, start, end))

        detailed.sort(key=lambda x: x[5])
        for step, detail in enumerate(detailed):
            ship_idx, task_id, base_idx, colon_idx, service, start, end = detail
            print(f"step: {step}, ship_idx: {ship_idx}, base_idx: {base_idx}, colon_idx: {colon_idx}, start: {start}, end: {end}")

def give_best_colon_for_base(capacities, num_colons, b, travel_matrix):
    candidates = [c for c in range(num_colons) if capacities[c] > 0]
    if not candidates:
        raise Exception('no capacities available')

    return min(candidates, key=lambda c: travel_matrix[b][c])


if __name__ == '__main__':
    # num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = get_input()
    num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
        3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [[6, 7, 8], [10, 9, 2], [6, 3, 7]])


    tasks: List[Tuple[int, int, int]] = []
    for b in range(num_bases):
        for _ in range(base[b]):
            best_colon = give_best_colon_for_base(capacities, num_colons, b, travel_matrix)
            tasks.append((b, best_colon, travel_matrix[b][best_colon]))
            capacities[best_colon] -= 1
    base_to_colon = tasks

    scheduler = Scheduler(num_ships, base_to_colon, to_base, matrix_time= travel_matrix)
    end_state = scheduler.search()

    print('endTime:', end_state.g)
    scheduler.print_schedule_with_stages(end_state)