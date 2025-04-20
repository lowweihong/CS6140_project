import time
from typing import List, Set, Tuple
from instance import SetCoverInstance, read_instance

def greedy_approximation(instance: SetCoverInstance) -> Tuple[List[int], int]:
    """
    Generate initial solution using greedy approximation.
    Uses set size heuristic for initial ordering.
    Returns 1-based indices.
    """
    solution = []
    covered = set()
    
    # Create list of (index, size) tuples and sort by size descending
    # Using 1-based indices
    set_sizes = [(i+1, len(instance.subsets[i])) for i in range(instance.m)]
    set_sizes.sort(key=lambda x: x[1], reverse=True)
    
    while covered != instance.universe:
        best_idx = -1
        best_coverage = 0
        
        # Iterate through sets in size-sorted order
        for idx, _ in set_sizes:
            if idx not in solution:
                # Convert to 0-based for subset access
                coverage = len(instance.subsets[idx-1] - covered)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_idx = idx
        
        if best_idx == -1 or best_coverage == 0:
            break
            
        solution.append(best_idx)
        # Convert index back to 0-based for subset access
        covered.update(instance.subsets[best_idx-1])
        
    return solution, len(solution)

def run_approximation(instance_path: str) -> Tuple[List[int], int, List[Tuple[float, int]]]:
    """Run greedy approximation algorithm with trace."""
    
    instance = read_instance(instance_path)
    return greedy_approximation(instance)