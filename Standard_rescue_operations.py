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
