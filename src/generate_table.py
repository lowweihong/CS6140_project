import glob
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def read_solution_file(filepath: str) -> Tuple[int, List[int]]:
    """Read solution file and return cost and solution."""
    with open(filepath, 'r') as f:
        cost = int(f.readline().strip())
        solution = list(map(int, f.readline().strip().split()))
    return cost, solution

def read_optimal_solutions() -> Dict[str, int]:
    """Read optimal solutions from instance files."""
    optimal_values = {}
    for instance_file in glob.glob("data/*.out"):
        instance_name = os.path.splitext(os.path.basename(instance_file))[0]
        # Read first line of instance file which contains optimal value
        with open(instance_file, 'r') as f:
            optimal_values[instance_name] = int(f.readline().split()[0])
    return optimal_values

def calculate_relative_error(value: float, optimal: float) -> float:
    """Calculate relative error (Alg - OPT)/OPT."""
    return (value - optimal) / optimal

def generate_results_table():
    """Generate comprehensive results table."""
    optimal_values = read_optimal_solutions()
    results = []

    # Load seeds from file
    try:
        seeds = np.loadtxt('seeds_ls.txt', dtype=int)
        print(f"Loaded {len(seeds)} seeds from seeds_ls.txt")
    except Exception as e:
        print(f"Error loading seeds: {e}")
        return
    
    # Process all instance files
    for instance_file in sorted(glob.glob("data/[ls]*.in")):  # small* and large* files
        print(instance_file)
        instance_name = os.path.splitext(os.path.basename(instance_file))[0]
        opt_value = optimal_values[instance_name]
        
        # For each algorithm
        for alg in ['Approx', 'LS1']:#['BnB', 'Approx', 'LS1', 'LS2']:
            # For local search, process multiple seeds
            if alg in ['LS1', 'LS2']:
                print(f"Processing {alg} for {instance_name}")
                costs = []
                times = []
                rel_errors = []  # Store relative errors for each run
                
                for seed in seeds:  # Process different seeds
                    sol_file = f"output/{instance_name}_{alg}_600_{seed}.sol"
                    print(sol_file)
                    if os.path.exists(sol_file):
                        print("File exists:", sol_file)
                        cost, _ = read_solution_file(sol_file)
                        costs.append(cost)
                        # Calculate relative error for this run
                        rel_errors.append(calculate_relative_error(cost, opt_value))
                        
                        # Read corresponding trace file for time
                        trace_file = f"output/{instance_name}_{alg}_600_{seed}.trace"
                        with open(trace_file, 'r') as f:
                            last_line = f.readlines()[-1]
                            time = float(last_line.split()[0])
                            times.append(time)
                
                print(f"Costs: {costs}")
                if costs:  # If we found any results
                    avg_cost = np.mean(costs)
                    avg_time = np.mean(times)
                    avg_rel_err = np.mean(rel_errors)  # Average of relative errors
                    results.append({
                        'Dataset': instance_name,
                        'Algorithm': alg,
                        'OPT': opt_value,
                        'Time (s)': f"{avg_time:.2f}",
                        'Collection Size': f"{avg_cost:.2f}",
                        'RelErr': f"{avg_rel_err:.2f}"
                    })
            else:
                # For BnB and Approx, just one result
                sol_file = f"output/{instance_name}_{alg}_600_42.sol"
                if os.path.exists(sol_file):
                    cost, _ = read_solution_file(sol_file)
                    if alg == 'BnB':
                        trace_file = f"output/{instance_name}_{alg}_600_42.trace"
                        with open(trace_file, 'r') as f:
                            last_line = f.readlines()[-1]
                            time = float(last_line.split()[0])
                    else:
                        time = 0.00  # Approx is instant
                    
                    rel_err = calculate_relative_error(cost, opt_value)
                    results.append({
                        'Dataset': instance_name,
                        'Algorithm': alg,
                        'OPT': opt_value,
                        'Time (s)': f"{time:.2f}",
                        'Collection Size': str(cost),
                        'RelErr': f"{rel_err:.2f}"
                    })
    
    # Convert to DataFrame and format as markdown
    df = pd.DataFrame(results)
    df.to_csv('results_LS1.csv', index=False)
    pivot_table = df.pivot_table(
        index='Dataset',
        columns='Algorithm',
        values=['Time (s)', 'OPT', 'Collection Size', 'RelErr'],
        aggfunc='first'
    )
    
    # print(pivot_table.to_markdown())
    # print(pivot_table)

if __name__ == "__main__":
    generate_results_table()