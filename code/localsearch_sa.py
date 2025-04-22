############################################
#### Local Search - Simulated Annealing#####
############################################


import time
import random
import math
from instance import read_instance
from typing import List, Tuple


def solve_approximation(universe, subsets):
    """
    Greedy approximation algorithm for the set cover problem.

    Args:
        universe (set): The set of all elements to be covered.
        subsets (list of sets): List of subsets available for covering.

    Returns:
        tuple: (cost, solution) where cost is the number of subsets used, 
               and solution is a list of indices of selected subsets.
    """
    uncovered = universe.copy()
    solution = []

    while uncovered:
        best_coverage = 0
        best_subset = -1

        for i in range(len(subsets)):
            if i not in solution:
                coverage = len(uncovered & subsets[i])
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_subset = i

        if best_subset != -1:
            solution.append(best_subset)
            uncovered -= subsets[best_subset]
        else:
            break

    return len(solution),solution



def run_simulated_annealing(instance_path: str, cutoff: int, seed: int) -> Tuple[List[int], int, List[Tuple[float, int]]]:
    """
    Local Search 2: Simulated Annealing

    Applies the Simulated Annealing metaheuristic to approximate a solution 
    to the Set Cover problem. The algorithm explores the solution space by 
    probabilistically accepting worse solutions to escape local minima, with 
    the probability decreasing as the temperature cools.

    Moreover, it will restart when the current cost is much worse than the previous best solution ever found.

    Args:
        time_limit (float): Time limit in seconds for the algorithm to run.
        seed (int): Random seed for reproducibility.
        universe (set): The set of all elements that need to be covered.
        subsets (list of sets): List of candidate subsets that can be selected to cover the universe.
        initial_cost (int): Cost (number of subsets used) of the initial solution.
        initial_solution (list of int): List of indices of subsets forming the initial solution.

    Returns:
        tuple:
            - best_solution (list of int): Indices of subsets selected in the best found solution.
            - trace (list of tuples): A list of (time, cost) tuples tracking the best cost achieved over time.
    """
    random.seed(seed)    

    start_time = time.time()
    trace = []
    instance = read_instance(instance_path)
    universe = instance.universe.copy()
    subsets = instance.subsets.copy()
    initial_cost, initial_solution = solve_approximation(universe, subsets)

    current_solution = set(initial_solution)
    current_cost = initial_cost
    best_solution = current_solution.copy()
    best_cost = current_cost

    trace.append((0, best_cost))

    initial_temp = 1.0
    final_temp = 0.01
    alpha = 0.95

    temp = initial_temp
    max_iterations_at_temp = 10000   

    while time.time() - start_time < cutoff and temp > final_temp:
        for _ in range(max_iterations_at_temp):
            if time.time() - start_time >= cutoff:
                break

            neighbor = current_solution.copy()
            if neighbor:
                to_remove = random.choice(list(neighbor))
                neighbor.remove(to_remove)

            uncovered = universe.copy()
            for j in neighbor:
                uncovered -= subsets[j]

            available_indices = [i for i in range(len(subsets)) if i not in neighbor]
            while uncovered and available_indices:
                best_idx = max(available_indices, key=lambda i: len(uncovered & subsets[i]))
                neighbor.add(best_idx)
                uncovered -= subsets[best_idx]
                available_indices.remove(best_idx)

            neighbor_cost = len(neighbor)            
            delta_from_best = neighbor_cost - best_cost
            delta_from_neighbor = neighbor_cost - current_cost

            if delta_from_best/best_cost >=0.5:
                current_solution = set(initial_solution)
                current_cost = initial_cost
            
            else:
                if delta_from_neighbor < 0 or random.random() < math.exp(-delta_from_neighbor / temp):
                    current_solution = neighbor
                    current_cost = neighbor_cost
                    if current_cost < best_cost:
                        best_solution = current_solution.copy()
                        best_cost = current_cost
                        elapsed = time.time() - start_time
                        trace.append((elapsed, best_cost))

        temp *= alpha       

    return list(best_solution), len(list(best_solution)),  trace