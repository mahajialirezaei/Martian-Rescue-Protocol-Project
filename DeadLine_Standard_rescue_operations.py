import heapq
from typing import List, Tuple, Dict, Optional


class State:
    def __init__(self,
                 times: List[float],
                 tasks_done: List[bool],
                 g: float,
                 f: float,
                 ship_prev_colons: Optional[List[int]] = None,
                 task_completion_times: Optional[List[Optional[float]]] = None,
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
        if task_completion_times is None:
            self.task_completion_times = [None] * len(tasks_done)
        else:
            self.task_completion_times = task_completion_times
        self.previous = previous
        self.action = action

    def __lt__(self, other):
        return self.f < other.f

    def __repr__(self):
        return f"State(g={self.g}, f={self.f}, times={self.times}, prev={self.ship_prev_colons})"


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
        rem.sort(reverse=True)
        est = sorted(times)
        for t in rem:
            est[0] += t
            est.sort()
        return max(est) - max(times)

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

    def search(self) -> Optional[State]:
        init_times = [0.0] * self.num_ships
        init_tasks_done = [False] * self.num_tasks
        init_ship_prev = [-1] * self.num_ships
        init_task_completion_times = [None] * self.num_tasks
        init_h = self.heuristic(init_tasks_done, init_times)
        init_state = State(times=init_times, tasks_done=init_tasks_done,
                           g=0.0, f=init_h,
                           ship_prev_colons=init_ship_prev,
                           task_completion_times=init_task_completion_times)

        ok, msg = self.check_deadlines_feasible_initial()
        if not ok:
            print("Initial feasibility check failed:", msg)
            return None

        heap: List[State] = []
        heapq.heappush(heap, init_state)
        watched: Dict[Tuple, float] = {}

        while heap:
            cur = heapq.heappop(heap)
            # goal test
            if all(cur.tasks_done):
                return cur

            key = (tuple(cur.tasks_done), tuple(cur.times), tuple(cur.ship_prev_colons),
                   tuple(cur.task_completion_times))
            if key in watched and watched[key] <= cur.g:
                continue
            watched[key] = cur.g

            # expand
            for tsk_id in range(self.num_tasks):
                if cur.tasks_done[tsk_id]:
                    continue
                base, colon, travel = self.jobs[tsk_id]
                for sh in range(self.num_ships):
                    new_times = cur.times.copy()
                    new_tasks_done = cur.tasks_done.copy()
                    new_tasks_done[tsk_id] = True
                    new_prev = cur.ship_prev_colons.copy()
                    new_task_completion = cur.task_completion_times.copy()

                    prev_col = new_prev[sh]
                    if prev_col == -1:
                        added = self.setup[base] + travel
                    else:
                        # cost = return from prev_col to base's "dock" and then to new colon (rule)
                        # we use matrix_time[base][prev_col] + travel
                        added = self.matrix_time[base][prev_col] + travel

                    new_times[sh] += added
                    new_prev[sh] = colon
                    new_task_completion[tsk_id] = new_times[sh]

                    new_g = max(cur.g, new_times[sh])
                    h = self.heuristic(new_tasks_done, new_times)

                    # Deadline pruning (optimistic)
                    # compute current completion per base from new_task_completion
                    cur_completion_per_base = {b: 0.0 for b in range(self.num_bases)}
                    for tidx, comp in enumerate(new_task_completion):
                        if comp is not None:
                            bidx, _, _ = self.jobs[tidx]
                            if comp > cur_completion_per_base[bidx]:
                                cur_completion_per_base[bidx] = comp

                    # remaining minimal services per base (optimistic per-task)
                    remaining_min_services = {b: [] for b in range(self.num_bases)}
                    for tidx, done in enumerate(new_tasks_done):
                        if not done:
                            bidx, _, trav = self.jobs[tidx]
                            # optimistic minimal service for this task:
                            min_return = min(self.matrix_time[bidx])
                            min_serv = trav + min(self.setup[bidx], min_return)
                            remaining_min_services[bidx].append(min_serv)

                    violates = False
                    # For each base with deadline, check if optimistic completion > dl
                    for b in range(self.num_bases):
                        dl = self.deadline[b]
                        if dl == -1:
                            continue
                        cur_comp = cur_completion_per_base[b]
                        rem = remaining_min_services[b]
                        if not rem:
                            if cur_comp > dl:
                                violates = True
                                break
                            else:
                                continue
                        # optimistic assignment of rem to current ship times
                        est_ships = sorted(new_times)
                        for serv in sorted(rem, reverse=True):
                            est_ships[0] += serv
                            est_ships.sort()
                        optimistic_completion = max(cur_comp, max(est_ships))
                        if optimistic_completion > dl:
                            violates = True
                            break

                    if violates:
                        continue

                    new_state = State(times=new_times, tasks_done=new_tasks_done,
                                      g=new_g, f=new_g + h,
                                      ship_prev_colons=new_prev,
                                      task_completion_times=new_task_completion,
                                      previous=cur, action=(sh, tsk_id))
                    heapq.heappush(heap, new_state)

        # no solution found
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
                f"step: {step}, ship_idx: {ship_idx}, base_idx: {base_idx}, colon_idx: {colon_idx}, start: {start}, end: {end}")


def give_best_colon_for_base(capacities, num_colons, b, travel_matrix):
    candidates = [c for c in range(num_colons) if capacities[c] > 0]
    if not candidates:
        raise Exception('no capacities available')
    return min(candidates, key=lambda c: travel_matrix[b][c])


if __name__ == '__main__':
    # num_ships, num_bases, num_colons, base, capacities, to_base, deadLine, travel_matrix = get_input()
    num_ships, num_bases, num_colons, base, capacities, to_base, deadLine, travel_matrix = (
        3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [-1, -1, 15], [[6, 7, 8], [10, 9, 2], [6, 3, 7]]
    )

    # build tasks (respect colony capacities)
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
