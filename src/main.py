import argparse
import sys
import time
from typing import List, Set, Tuple
from localsearch_hc import run_hill_climbing
from approximation import run_approximation
from localsearch_sa import run_simulated_annealing
from bnb import run_branch_and_bound

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Set Cover Problem Solver')
    
    parser.add_argument(
        '-inst',
        required=True,
        help='Path to the instance file'
    )
    
    parser.add_argument(
        '-alg',
        required=True,
        choices=['BnB', 'Approx', 'LS1', 'LS2'],
        help='Algorithm to use: Branch and Bound, Approximation, Local Search 1, or Local Search 2'
    )
    
    parser.add_argument(
        '-time',
        type=int,
        required=True,
        help='Cutoff time in seconds'
    )
    
    parser.add_argument(
        '-seed',
        type=int,
        required=True,
        help='Random seed for reproducibility'
    )
    
    return parser.parse_args()

def get_output_filename(instance_name: str, algorithm: str, cutoff: int, seed: int, ext: str) -> str:
    """Generate output filename in required format."""
    return f"{instance_name}_{algorithm}_{cutoff}_{seed}.{ext}"

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Set random seed
    import random
    random.seed(args.seed)
    
    try:
        # Read instance file
        instance_name = args.inst.split('/')[-1].split('.')[0]

        # Generate output filenames
        sol_file = get_output_filename(instance_name, args.alg, args.time, args.seed, "sol")
        trace_file = get_output_filename(instance_name, args.alg, args.time, args.seed, "trace")
        
        # Select and run algorithm
        if args.alg == 'BnB':
            solution, cost, trace = run_branch_and_bound(args.inst, args.time)
        elif args.alg == 'Approx':
            solution, cost = run_approximation(args.inst)
        elif args.alg == 'LS1':
            solution, cost, trace = run_hill_climbing(args.inst, args.time, args.seed)
        elif args.alg == 'LS2':
            solution, cost, trace = run_simulated_annealing(args.inst, args.time, args.seed)
        else: 
            raise ValueError("Invalid algorithm specified. Please choose from: BnB, Approx, LS1, LS2.")
            
            
        # Write solution and trace files
        write_solution(sol_file, solution, cost)
        if args.alg != 'Approx':
            write_trace(trace_file, trace)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def write_solution(filename: str, solution: List[int], cost: int):
    """Write solution to file."""
    with open(filename, 'w') as f:
        f.write(f"{cost}\n")
        f.write(" ".join(map(str, solution)))

def write_trace(filename: str, trace: List[Tuple[float, int]]):
    """Write solution trace to file."""
    with open(filename, 'w') as f:
        for timestamp, quality in trace:
            f.write(f"{timestamp:.2f} {quality}\n")

if __name__ == "__main__":
    main()