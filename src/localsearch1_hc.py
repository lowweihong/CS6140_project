import random
import time
from typing import List, Set, Tuple
from instance import SetCoverInstance, read_instance
from approximation import greedy_approximation

# Works with producing better results in ./data/test4.in 
def run_local_search1(instance_path: str, cutoff: int, seed: int) -> Tuple[List[int], int, List[Tuple[float, int]]]:
    """Fast Local Search with guided random swaps."""
    random.seed(seed)
    start_time = time.time()
    instance = read_instance(instance_path)
    print(f"Instance size: {instance.n} elements, {instance.m} subsets")

    greedy_solution, greedy_cost = greedy_approximation(instance)
    current_solution = greedy_solution.copy()
    current_cost = greedy_cost
    best_solution = current_solution.copy()
    best_cost = current_cost
    trace = [(0.0, current_cost)]

    subset_coverages = [set(s) for s in instance.subsets]

    no_improve_limit = 20
    no_improve_count = 0
    swap_sizes = [2, 3]
    max_subset_checks = 50  # only look at top 50 candidates to speed up


    while time.time() - start_time < cutoff and no_improve_count < no_improve_limit:
        improved = False

        for swap_size in swap_sizes:
            if len(current_solution) <= swap_size:
                continue

            # 1. Randomly remove 'swap_size' subsets
            remove_indices = random.sample(range(len(current_solution)), swap_size)
            temp_solution = [x for i, x in enumerate(current_solution) if i not in remove_indices]
            temp_coverage = set().union(*(subset_coverages[i - 1] for i in temp_solution))

            import pdb; pdb.set_trace()

            uncovered = instance.universe - temp_coverage
            if not uncovered:
                continue

            # 2. Look for candidate subsets to cover the uncovered
            candidates = []
            checked = 0
            for j in random.sample(range(1, instance.m + 1), instance.m):
                if j not in temp_solution:
                    gain = len(subset_coverages[j - 1] & uncovered)
                    if gain > 0:
                        candidates.append((j, gain))
                        checked += 1
                        if checked >= max_subset_checks:
                            break

            if not candidates:
                continue

            # 3. Select top few candidates to add
            candidates.sort(key=lambda x: -x[1])
            chosen = [x[0] for x in candidates[:swap_size]]

            new_solution = temp_solution + chosen
            new_coverage = set().union(*(subset_coverages[i - 1] for i in new_solution))

            if new_coverage == instance.universe and len(new_solution) <= current_cost:
                current_solution = new_solution
                current_cost = len(current_solution)
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
                    trace.append((time.time() - start_time, best_cost))
                improved = True
                no_improve_count = 0
                break

        if not improved:
            no_improve_count += 1
            # Fast "smart" restart from greedy + random tweak
            num_changes = random.choice([1, 2])

            # Ensures the greedy_solution has enough subsets to remove num_changes subsets
            if len(greedy_solution) > num_changes:
                remove_idx = random.sample(greedy_solution, num_changes)
                perturbed = [i for i in greedy_solution if i not in remove_idx]
                new_cov = set().union(*(subset_coverages[i - 1] for i in perturbed))
                uncovered = instance.universe - new_cov

                for j in range(1, instance.m + 1):
                    if j not in perturbed and uncovered & subset_coverages[j - 1]:
                        perturbed.append(j)
                        new_cov.update(subset_coverages[j - 1])
                        # if all elements are covered
                        if new_cov == instance.universe:
                            break

                if len(perturbed) < current_cost:
                    current_solution = perturbed
                    current_cost = len(current_solution)
                    no_improve_count = 0

        if time.time() - start_time > cutoff - 1:
            print("Approaching cutoff time, stopping search.")
            break

    print(f"{time.time() - start_time:.2f} seconds elapsed")
    return best_solution, best_cost, trace

def evaluate_solution(instance: SetCoverInstance, solution: List[int]) -> bool:
    """Verify if solution covers all elements."""
    covered = set()
    for idx in solution:
        covered.update(instance.subsets[idx])
    return covered == instance.universe

def generate_random_solution(instance: SetCoverInstance) -> List[int]:
    """Generate a random valid solution."""
    solution = []
    covered = set()
    remaining = set(range(instance.m))
    
    while covered != instance.universe and remaining:
        idx = random.choice(list(remaining))
        solution.append(idx)
        covered.update(instance.subsets[idx])
        remaining.remove(idx)
    
    return solution