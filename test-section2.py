import unittest
from typing import List, Tuple, Optional
import importlib
from DeadLine_Standard_rescue_operations import *
MODULE_NAME = "Standard_rescue_operations"


def best_colon_call(caps, num_colons, b, travel_matrix):
    fn = give_best_colon_for_base
    if fn is None:
        raise AttributeError("Module does not provide give_best_colon_for_base")
    try:
        return fn(caps, num_colons, b, travel_matrix)
    except TypeError:
        return fn(caps, num_colons, b)


def make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix):
    try:
        return Scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
    except Exception as e:
        raise TypeError(f"Could not construct Scheduler with known signatures: {e}")


def run_search(scheduler, travel_matrix):
    try:
        return scheduler.search()
    except TypeError:
        # maybe search expects matrix_time param
        return scheduler.search(travel_matrix)


class TestSection2Manual(unittest.TestCase):

    def build_tasks(self, num_bases, num_colons, base, capacities, travel_matrix):
        caps = capacities.copy()
        tasks: List[Tuple[int, int, int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best = best_colon_call(caps, num_colons, b, travel_matrix)
                tasks.append((b, best, travel_matrix[b][best]))
                caps[best] -= 1
        return tasks

    def assert_infeasible_or_none(self, scheduler, travel_matrix):
        try:
            res = run_search(scheduler, travel_matrix)
        except Exception:
            return
        self.assertIsNone(res, "Expected infeasible (None or exception), but search returned a schedule")

    def assert_search_makespan(self, scheduler, travel_matrix, expected):
        try:
            res = run_search(scheduler, travel_matrix)
        except Exception as e:
            self.fail(f"search() raised exception unexpectedly: {e}")
        self.assertIsNotNone(res, "Expected feasible schedule but got None")
        g_val = getattr(res, "g", None)
        self.assertIsNotNone(g_val, "Returned state has no attribute 'g'")
        self.assertEqual(expected, int(g_val), f"Expected makespan {expected}, got {g_val}")


    def test1_impossible_single_task_deadline(self):
        num_ships, num_bases, num_colons = 2, 2, 2
        base = [1, 1]
        capacities = [1, 1]
        to_base = [2, 3]
        travel_matrix = [[3, 1], [2, 2]]
        deadLine = [-1, 4]
        tasks = self.build_tasks(num_bases, num_colons, base, capacities, travel_matrix)
        sched = make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
        print(sched)

        self.assert_infeasible_or_none(sched, travel_matrix)

    def test2_three_ships_base2_deadline(self):
        num_ships, num_bases, num_colons = 3, 3, 3
        base = [1, 1, 1]
        capacities = [1, 1, 1]
        to_base = [4, 2, 3]
        travel_matrix = [[1, 2, 3], [2, 1, 1], [3, 2, 1]]
        deadLine = [-1, -1, 4]
        tasks = self.build_tasks(num_bases, num_colons, base, capacities, travel_matrix)
        sched = make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
        self.assert_search_makespan(sched, travel_matrix, expected=5)

    def test3_five_bases_deadline_base2(self):
        num_ships, num_bases, num_colons = 3, 5, 3
        base = [1, 1, 1, 1, 1]
        capacities = [2, 2, 1]
        to_base = [2, 1, 2, 1, 2]
        travel_matrix = [
            [1, 3, 4],
            [2, 1, 3],
            [3, 2, 1],
            [1, 2, 2],
            [2, 1, 1],
        ]
        deadLine = [-1, -1, 3, -1, -1]
        tasks = self.build_tasks(num_bases, num_colons, base, capacities, travel_matrix)
        sched = make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
        self.assert_search_makespan(sched, travel_matrix, expected=4)

    def test4_project_example_impossible(self):
        num_ships, num_bases, num_colons = 3, 3, 3
        base = [1, 3, 3]
        capacities = [4, 4, 1]
        to_base = [7, 4, 9]
        travel_matrix = [
            [6, 7, 8],
            [10, 9, 2],
            [6, 3, 7],
        ]
        deadLine = [-1, -1, 10]
        tasks = self.build_tasks(num_bases, num_colons, base, capacities, travel_matrix)
        sched = make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
        self.assert_infeasible_or_none(sched, travel_matrix)

    def test5_two_ships_deadline_on_base1(self):
        num_ships, num_bases, num_colons = 2, 3, 3
        base = [1, 1, 1]
        capacities = [1, 1, 1]
        to_base = [2, 5, 1]
        travel_matrix = [
            [1, 4, 3],
            [2, 1, 5],
            [3, 2, 1],
        ]
        deadLine = [-1, 7, -1]
        tasks = self.build_tasks(num_bases, num_colons, base, capacities, travel_matrix)
        sched = make_scheduler(num_ships, tasks, to_base, deadLine, travel_matrix)
        self.assert_search_makespan(sched, travel_matrix, expected=6)


if __name__ == "__main__":
    unittest.main()
