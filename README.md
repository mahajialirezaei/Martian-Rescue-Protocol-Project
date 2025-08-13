# Martian Rescue — Scheduling & Deadline-aware Scheduling (A\* based)

A compact Python project that implements A*-style schedulers for a multi-ship rescue/transport problem.
Two solver modules are provided: a standard scheduler (no per-base deadlines) and a deadline-aware variant that performs initial feasibility checks and enforces base-specific deadlines during search. The project also includes unit tests that exercise example scenarios and edge cases.

---

## Key ideas / problem statement

* We have several **ships**, several **bases**, and several **colonies** (colon).
* Each base has a number of groups (tasks) that must be delivered to colonies. Colonies have finite capacities.
* Each task is represented as `(base_index, colony_index, travel_time)`.
* Each ship performs a sequence of services; service time depends on whether the ship starts from base (setup time) or returns from its previous colony (matrix travel time).
* Objective: assign tasks to ships and order them to **minimize the overall makespan** (finish time when all tasks are done).
* The deadline-aware variant also enforces **per-base deadlines**: all tasks that originate from a base must be completed (boarding time) no later than that base's deadline.

---

## Algorithms & implementation notes

* Both solvers use a best-first A\* search over partial schedules (states).
* **State representation** includes:

  * `times`: current finish time per ship,
  * `tasks_done`: boolean mask of completed tasks,
  * `ship_previous_colons`: last colon visited by each ship,
  * (deadline variant) `task_boarding_times`: boarding/start times per task,
  * `g`: current makespan,
  * `f = g + h`: A\* evaluation with an admissible heuristic.
* **Admissible heuristic**: estimates remaining work by computing a lower bound per remaining job (`min_service`) and distributing these lower bounds optimistically across ships (a simple multiprocessor load-balancing lower bound). This keeps the search admissible and prunes many branches.
* **Deadline-aware module**:

  * Computes `min_service` similarly.
  * Performs an **initial feasibility check** per base: if even an optimistic scheduling of that base’s services exceeds its deadline, the instance is reported infeasible early.
  * While expanding a state, it also computes optimistic completion (boarding) times for remaining jobs per base and prunes any assignment that cannot meet a base deadline.
* Utility function `give_best_colon_for_base(...)` greedily assigns each base group to the nearest available colony (respecting colony capacities) when building the task list for a scenario.

---

## Files in this directory

* `Standard_rescue_operations.py`
  Main scheduler without per-base deadlines. Implements `Scheduler`, `State`, `give_best_colon_for_base`, and a `__main__` sample run.
* `DeadLine_Standard_rescue_operations.py`
  Deadline-aware scheduler. Adds initial feasibility checks, boarding-time bookkeeping, and deadline pruning during search.
* `test_section1.py` / `test-section1.py`
  Unit tests for the *standard* (no-deadline) scheduler — several small scenarios and the canonical project example.
* `test_section2.py` / `test-section2.py`
  Unit tests for the *deadline-aware* scheduler — tests for feasibility, deadline enforcement and expected makespans.

---

## Requirements

* Python 3.8+ (standard library only — `heapq`, `typing`, `unittest` are used).
* No external dependencies required for core functionality. `pytest` may be used for running tests if you prefer it.

---

## How to run

Run a simple example (module contains a small `__main__` test case):

```bash
# run standard scheduler example
python Standard_rescue_operations.py

# run deadline-aware scheduler example
python DeadLine_Standard_rescue_operations.py
```


```
endTime: 23
step: 0, ship_idx: 0, base_idx: 1, colon_idx: 2, start: 0.0, end: 7.0
...
```

---

## Running tests

With `unittest` (built-in):

```bash
# run all tests discovered in current directory
python -m unittest discover -v
```

Or run a specific test file:

```bash
python -m unittest test_section1.py
python -m unittest test_section2.py
```

With `pytest` (if installed):

```bash
pytest -q
```

---

## Example workflow (how tasks are built)

1. Input describing number of ships, bases, colonies, group counts per base, colony capacities, `to_base` setup times and the travel matrix is read (or hard-coded in the `__main__` examples).
2. For each base group, `give_best_colon_for_base` picks the nearest available colony (respecting capacities) and produces a `tasks` list.
3. `Scheduler(...).search()` runs the A* search and returns a final `State` (or `None` if infeasible for the deadline-aware variant).
4. `print_schedule_with_stages` prints an ordered list of actions with start/end times and which ship performed them.

---


## 🛠 Developer

Developed by [Mohammad Amin Haji Alirezaei](https://github.com/mahajialirezaei)
Feel free to ⭐️ this repo or open an issue if you'd like to contribute or have questions!
