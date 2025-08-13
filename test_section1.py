import unittest
from typing import List, Tuple
from Standard_rescue_operations import give_best_colon_for_base, Scheduler

class TestSection1Manual(unittest.TestCase):
    def test_case_1_project_example(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9],
            [[6, 7, 8], [10, 9, 2], [6, 3, 7]]
        )
        caps = capacities.copy()
        tasks: List[Tuple[int,int,int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_1")
        self.assertEqual(23, int(end_state.g), msg=f"Expected 23, got {end_state.g}")

    def test_case_2_simple_2ships(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            2, 2, 2, [1, 1], [1, 1], [2, 3], [[3,1], [2,2]]
        )
        caps = capacities.copy()
        tasks: List[Tuple[int,int,int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_2")
        self.assertEqual(5, int(end_state.g), msg=f"Expected 5, got {end_state.g}")

    def test_case_3_three_ships_distinct(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            3, 3, 3, [1,1,1], [1,1,1], [4,2,3],
            [[1,2,3],[2,1,1],[3,2,1]]
        )
        caps = capacities.copy()
        tasks: List[Tuple[int,int,int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_3")
        self.assertEqual(5, int(end_state.g), msg=f"Expected 5, got {end_state.g}")

    def test_case_4_four_bases_two_ships(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            2, 4, 2, [1,1,1,1], [2,2], [1,1,1,1],
            [[1,2],[2,1],[1,1],[2,2]]
        )
        caps = capacities.copy()
        tasks: List[Tuple[int,int,int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_4")
        self.assertEqual(5, int(end_state.g), msg=f"Expected 5, got {end_state.g}")

    def test_case_5_five_bases_three_ships(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            3, 5, 3, [1,1,1,1,1], [2,2,1], [2,1,2,1,2],
            [[1,3,4],[2,1,3],[3,2,1],[1,2,2],[2,1,1]]
        )
        caps = capacities.copy()
        tasks: List[Tuple[int,int,int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_5")
        self.assertEqual(4, int(end_state.g), msg=f"Expected 5, got {end_state.g}")


    def test_case_6_five_bases_three_ships(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
        4, 4, 4, [1, 3, 3, 4], [4, 4, 1, 4], [7, 4, 9, 2],
        [[6, 7, 8, 3], [10, 9, 2, 4], [6, 3, 7, 5], [6, 7, 8, 9]])

        caps = capacities.copy()
        tasks: List[Tuple[int, int, int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(caps, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                caps[best_colon] -= 1
        scheduler = Scheduler(num_ships, tasks, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertIsNotNone(end_state, "No schedule found for test_case_5")
        self.assertEqual(24, int(end_state.g), msg=f"Expected 24, got {end_state.g}")


if __name__ == '__main__':
    unittest.main()
