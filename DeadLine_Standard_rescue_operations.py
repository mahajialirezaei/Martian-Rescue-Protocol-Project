import heapq
import math
from typing import List, Tuple, Dict, Optional


class State:
    def __init__(self,
                 times: List[float],
                 tasks_done: List[bool],
                 g: float,
                 f: float,
                 ship_prev_colons: Optional[List[int]] = None,
                 task_boarding_times: Optional[List[Optional[float]]] = None,
                 previous=None,
                 action=None):
        self.times = times
        self.tasks_done = tasks_done
        self.g = g
        self.f = f
        if ship_prev_colons is None:
            self.ship_prev_colons = [-1] * len(times)
        else:
            self.ship_prev_colons = ship_prev_colons
        if task_boarding_times is None:
            self.task_boarding_times = [None] * len(tasks_done)
        else:
            self.task_boarding_times = task_boarding_times
        self.previous = previous
        self.action = action

    def __lt__(self, other):
        return self.f < other.f

    def __repr__(self):
        return f"State(g={self.g:.1f}, f={self.f:.1f}, times={self.times}, prev={self.ship_prev_colons})"


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
                 base_to_colon: List[Tuple[int, int, int]],
                 texas_to_base: List[int],
                 deadLine: List[int],
                 matrix_time: List[List[int]]):
        self.num_ships = num_ships
        self.jobs = base_to_colon
        self.setup = texas_to_base
        self.deadline = deadLine
        self.matrix_time = matrix_time
        self.num_tasks = len(self.jobs)
        self.num_bases = len(matrix_time)
        self.min_service = []
        for (b, c, travel) in self.jobs:
            min_return = min(self.matrix_time[b])
            self.min_service.append(travel + min(self.setup[b], min_return))

    def heuristic(self, tasks_done: List[bool], times: List[float]) -> float:
        rem = [self.min_service[i] for i, done in enumerate(tasks_done) if not done]
        if not rem:
            return 0.0
        total_remaining = sum(rem)
        m = self.num_ships
        LB_final = max(max(times), math.ceil((sum(times) + total_remaining) / m))
        return max(0.0, LB_final - max(times))

    def greedy_initial_solution(self) -> float:
        times = [0.0] * self.num_ships
        prev = [-1] * self.num_ships
        boarding_times = [None] * self.num_tasks
        base_dead = {b: (self.deadline[b] if b < len(self.deadline) else -1) for b in range(self.num_bases)}
        order = list(range(self.num_tasks))
        order.sort(key=lambda tid: (base_dead[self.jobs[tid][0]] if base_dead[self.jobs[tid][0]] != -1 else 1e9,
                                    -self.min_service[tid]))

        for tid in order:
            sh = min(range(self.num_ships), key=lambda s: times[s])
            b, c, travel = self.jobs[tid]
            if prev[sh] == -1:
                boarding = times[sh] + self.setup[b]
            else:
                boarding = times[sh] + self.matrix_time[b][prev[sh]]
            arrival = boarding + travel
            times[sh] = arrival
            prev[sh] = c
            boarding_times[tid] = boarding
            dl = self.deadline[b] if b < len(self.deadline) else -1
            if dl != -1 and boarding > dl:
                return math.inf

        return max(times)

    def check_deadlines_feasible_initial(self) -> Tuple[bool, str]:
        base_services: Dict[int, List[float]] = {b: [] for b in range(self.num_bases)}
        for tid, (b, c, travel) in enumerate(self.jobs):
            base_services[b].append(self.min_service[tid])
        for b, dl in enumerate(self.deadline):
            if dl == -1:
                continue
            services = base_services.get(b, [])
            if not services:
                continue
            if min(services) > dl:
                return False, f"Base {b}: single cheapest service {min(services)} > deadline {dl}"
            est = [0.0] * self.num_ships
            for serv in sorted(services, reverse=True):
                i = est.index(min(est))
                est[i] += serv
            if max(est) > dl:
                return False, f"Base {b}: even optimistic all-ships dedicated makespan {max(est)} > deadline {dl}"
        return True, ""

    def canonical_key(self, tasks_done: List[bool], times: List[float], prev_cols: List[int],
                      task_boarding_times: List[Optional[float]]) -> Tuple:

        pairs = tuple(sorted(zip(times, prev_cols)))
        return (tuple(tasks_done), pairs, tuple(task_boarding_times))

    def search(self) -> Optional[State]:
        init_times = [0.0] * self.num_ships
        init_tasks_done = [False] * self.num_tasks
        init_ship_prev = [-1] * self.num_ships
        init_task_boarding = [None] * self.num_tasks
        init_h = self.heuristic(init_tasks_done, init_times)
        init_state = State(times=init_times, tasks_done=init_tasks_done, g=0.0, f=init_h,
                           ship_prev_colons=init_ship_prev, task_boarding_times=init_task_boarding)

        ok, msg = self.check_deadlines_feasible_initial()
        if not ok:
            print("Initial feasibility check failed:", msg)
            return None

        incumbent = self.greedy_initial_solution()
        heap: List[State] = []
        heapq.heappush(heap, init_state)
        watched: Dict[Tuple, float] = {}

        while heap:
            cur = heapq.heappop(heap)
            if all(cur.tasks_done):
                if cur.g < incumbent:
                    incumbent = cur.g
                return cur

            if incumbent != math.inf and cur.g > incumbent:
                continue

            key = self.canonical_key(cur.tasks_done, cur.times, cur.ship_prev_colons, cur.task_boarding_times)
            if key in watched and watched[key] <= cur.g:
                continue
            watched[key] = cur.g

            for tsk_id in range(self.num_tasks):
                if cur.tasks_done[tsk_id]:
                    continue
                base, colon, travel = self.jobs[tsk_id]
                for sh in range(self.num_ships):
                    new_times = cur.times.copy()
                    new_tasks_done = cur.tasks_done.copy()
                    new_tasks_done[tsk_id] = True
                    new_prev = cur.ship_prev_colons.copy()
                    new_task_boarding = cur.task_boarding_times.copy()
                    start = cur.times[sh]
                    prev_col = new_prev[sh]
                    if prev_col == -1:
                        boarding_time = start + self.setup[base]
                        arrival_time = boarding_time + travel
                    else:
                        boarding_time = start + self.matrix_time[base][prev_col]
                        arrival_time = boarding_time + travel

                    new_times[sh] = arrival_time
                    new_prev[sh] = colon
                    new_task_boarding[tsk_id] = boarding_time

                    new_g = max(cur.g, new_times[sh])
                    h = self.heuristic(new_tasks_done, new_times)

                    cur_boarding_per_base = {b: 0.0 for b in range(self.num_bases)}
                    for tidx, bt in enumerate(new_task_boarding):
                        if bt is not None:
                            bidx, _, _ = self.jobs[tidx]
                            if bt > cur_boarding_per_base[bidx]:
                                cur_boarding_per_base[bidx] = bt

                    remaining_min_services = {b: [] for b in range(self.num_bases)}
                    for tidx, done in enumerate(new_tasks_done):
                        if not done:
                            bidx, _, trav = self.jobs[tidx]
                            min_return = min(self.matrix_time[bidx])
                            min_serv = trav + min(self.setup[bidx], min_return)
                            remaining_min_services[bidx].append(min_serv)

                    violates = False
                    for b in range(self.num_bases):
                        dl = self.deadline[b]
                        if dl == -1:
                            continue
                        cur_boarding = cur_boarding_per_base[b]
                        rem = remaining_min_services[b]
                        if not rem:
                            if cur_boarding > dl:
                                violates = True
                                break
                            else:
                                continue
                        est_ships = sorted(new_times)
                        boarding_times_for_b = []
                        for serv in sorted(rem, reverse=True):
                            earliest = est_ships[0]
                            boarding_times_for_b.append(earliest)
                            est_ships[0] += serv
                            est_ships.sort()
                        optimistic_boarding_completion = max(cur_boarding, max(boarding_times_for_b))
                        if optimistic_boarding_completion > dl:
                            violates = True
                            break

                    if violates:
                        continue

                    if incumbent != math.inf and new_g + h > incumbent:
                        continue

                    new_state = State(times=new_times, tasks_done=new_tasks_done,
                                      g=new_g, f=new_g + h,
                                      ship_prev_colons=new_prev,
                                      task_boarding_times=new_task_boarding,
                                      previous=cur, action=(sh, tsk_id))
                    heapq.heappush(heap, new_state)

        return None

    def reconstruct(self, end_state: State) -> List[Tuple[int, int]]:
        path: List[Tuple[int, int]] = []
        s = end_state
        while s.previous is not None:
            path.append(s.action)
            s = s.previous
        return list(reversed(path))

    def print_schedule_with_stages(self, end_state: State):
        schedule = self.reconstruct(end_state)
        base_to_colon = self.jobs
        cur_times = [0.0] * self.num_ships
        prev_col = [-1] * self.num_ships
        detailed = []

        for (ship_idx, task_id) in schedule:
            base_idx, colon_idx, travel = base_to_colon[task_id]
            if prev_col[ship_idx] == -1:
                service = self.setup[base_idx] + travel
            else:
                service = self.matrix_time[base_idx][prev_col[ship_idx]] + travel
            start = cur_times[ship_idx]
            end = start + service
            cur_times[ship_idx] = end
            prev_col[ship_idx] = colon_idx
            detailed.append((ship_idx, task_id, base_idx, colon_idx, service, start, end))

        detailed.sort(key=lambda x: x[5])
        for step, detail in enumerate(detailed):
            ship_idx, task_id, base_idx, colon_idx, service, start, end = detail
            print(
                f"step: {step}, ship_idx: {ship_idx}, base_idx: {base_idx}, colon_idx: {colon_idx}, start: {start}, end: {end}"
            )


def give_best_colon_for_base(capacities, num_colons, b, travel_matrix):
    candidates = [c for c in range(num_colons) if capacities[c] > 0]
    if not candidates:
        raise Exception('no capacities available')
    return min(candidates, key=lambda c: travel_matrix[b][c])


if __name__ == '__main__':
    # example (from your conversation)
    num_ships, num_bases, num_colons, base, capacities, to_base, deadLine, travel_matrix = (
        3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [-1, -1, 10], [[6, 7, 8], [10, 9, 2], [6, 3, 7]]
    )

    tasks: List[Tuple[int, int, int]] = []
    caps = capacities.copy()
    for b in range(num_bases):
        for _ in range(base[b]):
            best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
            tasks.append((b, best_colon, travel_matrix[b][best_colon]))
            caps[best_colon] -= 1

    scheduler = Scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
    end_state = scheduler.search()

    if end_state is None:
        print("No feasible schedule found (respecting deadlines).")
    else:
        print("endTime:", end_state.g)
        scheduler.print_schedule_with_stages(end_state)
