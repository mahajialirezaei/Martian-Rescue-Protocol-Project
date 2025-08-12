import unittest
from Standard_rescue_operations import *


class MyTestCase(unittest.TestCase):
    def test_case1(self):
        num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (
            3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [[6, 7, 8], [10, 9, 2], [6, 3, 7]])
        tasks: List[Tuple[int, int, int]] = []
        for b in range(num_bases):
            for _ in range(base[b]):
                best_colon = give_best_colon_for_base(capacities, num_colons, b, travel_matrix)
                tasks.append((b, best_colon, travel_matrix[b][best_colon]))
                capacities[best_colon] -= 1
        base_to_colon = tasks
        scheduler = Scheduler(num_ships, base_to_colon, to_base, matrix_time=travel_matrix)
        end_state = scheduler.search()
        self.assertEqual(23, end_state.g, msg='Wasn\'t equal to 23 it was' + str(end_state.g))


if __name__ == '__main__':
    unittest.main()
