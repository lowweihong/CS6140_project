import time
from queue import PriorityQueue
from typing import List, Tuple
from instance import read_instance


def greedy_set_cover(universe, sets):
    """
    Greedy algorithm to approximate set cover.

    Args:
        universe (set): The set of all elements to be covered.
        sets (List[set]): List of subsets that can be used to cover the universe.

    Returns:
        List[int]: List of indices of the selected subsets.
    """

    uncovered = universe.copy()
    cover = []
    used_indices = set()

    while uncovered:
        best_index = max(
            range(len(sets)),
            key=lambda i: len(sets[i] & uncovered) if i not in used_indices else -1
        )
        best_set = sets[best_index]
        if not best_set & uncovered:
            break
        cover.append(best_index)
        uncovered -= best_set
        used_indices.add(best_index)

    return cover


def branch_and_bound(universe, sets, cutoff):
    """
    Branch and Bound algorithm to solve the Set Cover problem.

    Args:
        instance (SetCoverInstance): Object containing the universe and subsets.
        cutoff (int): Time limit in seconds for the algorithm to run.

    Returns:
        Tuple[List[int], int, List[Tuple[float, int]]]: A tuple containing:
            1. List of selected subset indices.
            2. Cost of the solution (number of subsets).
            3. Trace of (time, cost) for solution updates.
    """

    start_time = time.time()
    best_solution = None
    best_cost = float('inf')
    trace = []

    greedy_solution = greedy_set_cover(universe, sets)
    upper_bound = len(greedy_solution)
    best_solution = greedy_solution[:]
    best_cost = upper_bound
    trace.append((0.0, best_cost))

    m = len(sets)
    queue = PriorityQueue()
    queue.put((0, [], set(), set(range(m))))  # (priority, selected, covered, undecided)

    MAX_QUEUE = 800000
    check_interval = 10000
    iteration = 0

    while not queue.empty() and time.time() - start_time < cutoff:
        iteration += 1
        if iteration % check_interval == 0:
            print(f"[{time.strftime('%H:%M:%S')}] Queue size: {queue.qsize()}")

        if queue.qsize() > MAX_QUEUE:
            continue

        lb, selected, covered, undecided = queue.get()

        if lb >= best_cost:
            continue

        if covered == universe:
            if len(selected) < best_cost:
                best_cost = len(selected)
                best_solution = selected[:]
                trace.append((time.time() - start_time, best_cost))
            continue

        if not undecided:
            continue

        i = next(iter(undecided))
        remaining = undecided - {i}

        new_selected = selected + [i]
        new_covered = covered | sets[i]
        gain = len(sets[i] & (universe - covered))
        new_lb = len(new_selected)
        priority = new_lb - gain * 0.01  # favor higher gain

        if new_lb < best_cost and new_covered != covered and queue.qsize() < MAX_QUEUE:
            queue.put((priority, new_selected, new_covered, remaining))

        if lb < best_cost and queue.qsize() < MAX_QUEUE:
            queue.put((lb, selected, covered, remaining))

    return best_solution, best_cost, trace


def run_branch_and_bound(instance_path: str, cutoff: int) -> Tuple[List[int], int, List[Tuple[float, int]]]:
    """"
    Run greedy approximation algorithm with trace.

    Args:
        instance_path (str): Path to the file containing the set cover instance.

    Returns:
        Tuple[List[int], int]: A tuple containing:
            1. A list of 1-based indices of the subsets selected to cover the universe.
            2. The number of subsets used (cost of the solution).
    """

    instance = read_instance(instance_path)
    solution, cost, trace = branch_and_bound(instance.universe, instance.subsets, cutoff)
    return solution, cost, trace
