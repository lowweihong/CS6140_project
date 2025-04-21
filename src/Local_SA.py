############################################
#### Local Search - Simulated Annealing#####
############################################

import argparse
import time
import random
import os
import math
from approximation import solve_approximation

def solve_Simulated_Annealing(time_limit, seed, universe, subsets, initial_cost, initial_solution):
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

    while time.time() - start_time < time_limit and temp > final_temp:
        for _ in range(max_iterations_at_temp):
            if time.time() - start_time >= time_limit:
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

    return list(best_solution), trace


def read_input(filename):
    """
    Read the set cover problem from file
    
    Args:
        filename: Path to input file
        
    Returns:
        universe: Set of elements
        subsets: List of subsets
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    n, m = map(int, lines[0].strip().split())
    universe = set(range(1, n+1))
    subsets = []
    
    for i in range(1, m+1):
        subset_data = list(map(int, lines[i].strip().split()))        
        subset = set(subset_data[1:])
        subsets.append(subset)
        
    return universe, subsets

def write_solution(filename, selected_subsets):
    """
    Write solution to file
    
    Args:
        filename: Path to output file
        selected_subsets: List of indices of selected subsets
    """
    with open(filename, 'w') as f:
        f.write(f"{len(selected_subsets)}\n")        
        subset_indices = ' '.join(str(i+1) for i in sorted(selected_subsets))
        f.write(f"{subset_indices}\n")

def write_trace(filename, trace):
    """
    Write solution trace to file
    
    Args:
        filename: Path to output file
        trace: List of (time, quality) tuples
    """
    with open(filename, 'w') as f:
        for elapsed, quality in trace:
            f.write(f"{elapsed:.2f} {quality}\n")

def main():
    parser = argparse.ArgumentParser(description='Minimum Set Cover Solver')
    parser.add_argument('-inst', required=False, default="*.in", help='Instance file path')
    parser.add_argument('-alg', required=False, choices=['BnB', 'Approx', 'HC', 'SA'], default="SA", help='Algorithm to use')
    parser.add_argument('-time', type=float, required=False, default=60, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, nargs='+', required=False, default=list(range(1, 3)), help='Random seeds')
    
    args = parser.parse_args()    
    file_paths = args.inst
    cutoff = args.time

    for file_path in file_paths:
        instance_name = os.path.basename(file_path).split('.')[0]        
        universe, subsets = read_input(file_path)
        approx_cost, approx_solution = solve_approximation(universe, subsets)

        if args.alg == 'SA':
            for seed in args.seed:
                solution, trace = solve_Simulated_Annealing(cutoff, seed, universe, subsets, approx_cost, approx_solution)

                sol_file = f"{instance_name}_SA_{int(cutoff)}_{seed}.sol"
                trace_file = f"{instance_name}_SA_{int(cutoff)}_{seed}.trace"

                write_solution(sol_file, solution)
                write_trace(trace_file, trace)
   

if __name__ == "__main__":
    main()