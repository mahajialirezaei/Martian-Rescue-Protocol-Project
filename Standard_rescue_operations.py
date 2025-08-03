import heapq
from typing import List, Tuple, Dict


class State:
    def __init__(self,
                 times: List[float],
                 tasks_done: int,
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


if __name__ == '__main__':
    # num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = get_input()
    num_ships, num_bases, num_colons, base, capacities, to_base, travel_matrix = (3, 3, 3, [1, 3, 3], [4, 4, 1], [7, 4, 9], [[6, 7, 8], [10, 9, 2], [6, 3, 7]])
    tasks: List[Tuple[int, int, int]] = []


    for b in range(num_bases):
        for _ in range(base[b]):
            c_best = min(range(num_colons), key=lambda c: travel_matrix[b][c])
            tasks.append((b, c_best, travel_matrix[b][c_best]))
            capacities[c_best] -= 1
    base_to_colon = tasks

