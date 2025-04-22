from typing import List, Tuple
from instance import SetCoverInstance, read_instance

def greedy_approximation(instance: SetCoverInstance) -> Tuple[List[int], int]:
    """"
    Greedy approximation algorithm for the set cover problem.

    Args:
        instance (SetCoverInstance): An instance of the set cover problem containing the universe of elements and a list of subsets.

    Returns:
        Tuple[List[int], int]: A tuple containing:
            1. A list of 1-based indices of the selected subsets forming the cover.
            2. The number of subsets used (cost of the solution).
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

def run_approximation(instance_path: str) -> Tuple[List[int], int]:
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
    return greedy_approximation(instance)