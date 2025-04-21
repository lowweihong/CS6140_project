import random
import time
from typing import List, Set, Tuple
from instance import SetCoverInstance, read_instance
from approximation import greedy_approximation

def run_hill_climbing(instance_path: str, cutoff: int, seed: int) -> Tuple[List[int], int, List[Tuple[float, int]]]:
    """
    Runs an improved local search algorithm to solve the Set Cover problem.

    Args:
        instance_path: Path to the input instance file.
        cutoff: Maximum running time in seconds.
        seed: Random seed for reproducibility.

    Returns:
        A tuple containing:
            - The best solution found (list of subset indices),
            - The cost (length) of the best solution,
            - Trace of (time, cost) for solution updates.
    """
    random.seed(seed)
    start_time = time.time()
    instance = read_instance(instance_path)
    print(f"Instance size: {instance.n} elements, {instance.m} subsets")

    # Initialize with greedy solution
    greedy_solution, greedy_cost = greedy_approximation(instance)
    current_solution = greedy_solution.copy()
    current_cost = greedy_cost
    best_solution = current_solution.copy()
    best_cost = current_cost
    trace = [(0.0, current_cost)]

    # Precompute subset coverages
    subset_coverages = [set(s) for s in instance.subsets]

    # Maintain coverage count for each element
    coverage_count = [0] * instance.n
    for idx in current_solution:
        for elem in subset_coverages[idx - 1]:
            coverage_count[elem - 1] += 1

    no_improve_limit = 20
    no_improve_count = 0
    max_subset_checks = 50
    swap_size = 1  # Start with small swaps
    max_swap_size = max(2, int(0.1 * len(current_solution)))  # Cap at 10% of solution size

    def get_uncovered_elements():
        """
        Returns a set of currently uncovered elements in the universe
        based on the current `coverage_count`.
        """
        return {i + 1 for i, count in enumerate(coverage_count) if count == 0}

    def update_coverage(add_idx=None, remove_idx=None):
        """
        Incrementally updates `coverage_count` when adding or removing subsets.

        Args:
            solution: Current list of selected subsets.
            add_idx: Index of subset to add to the solution.
            remove_idx: Index of subset to remove from the solution.
        """
        if remove_idx is not None:
            for elem in subset_coverages[remove_idx - 1]:
                coverage_count[elem - 1] -= 1
        if add_idx is not None:
            for elem in subset_coverages[add_idx - 1]:
                coverage_count[elem - 1] += 1

    while time.time() - start_time < cutoff:

        # Calculate exclusive coverage for each subset in solution
        exclusive_coverage = []
        for i, idx in enumerate(current_solution):
            exclusive_count = sum(1 for elem in subset_coverages[idx - 1] if coverage_count[elem - 1] == 1)
            exclusive_coverage.append((i, idx, exclusive_count))

        # Sort by exclusive coverage (low to high) to prioritize removing less critical subsets
        exclusive_coverage.sort(key=lambda x: x[2])

        # Try removing subsets with low exclusive coverage
        remove_count = min(swap_size, len(current_solution))
        remove_indices = [exclusive_coverage[i][0] for i in range(min(remove_count, len(exclusive_coverage)))]
        remove_subsets = [exclusive_coverage[i][1] for i in range(min(remove_count, len(exclusive_coverage)))]

        # temp solution: list after subsets are removed
        temp_solution = [x for i, x in enumerate(current_solution) if i not in remove_indices]
        for idx in remove_subsets:
            # update coverage after removing the subset
            update_coverage(remove_idx=idx)

        # check if removal improve solution
        uncovered = get_uncovered_elements()
        if not uncovered and len(temp_solution) < current_cost:
            # Solution is valid and better
            current_solution = temp_solution
            current_cost = len(current_solution)
            if current_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = current_cost
                trace.append((time.time() - start_time, best_cost))
                no_improve_count = 0
                swap_size = 1  # Reset swap size
                print(f"Improved solution: cost={current_cost}")
            continue

        # Find candidates to cover uncovered elements
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
        
        # if no candidates subset that is able to cover uncovered elements
        if not candidates:
            # Restore coverage and try larger swap
            for idx in remove_subsets:
                update_coverage(add_idx=idx)
            swap_size = min(swap_size + 1, max_swap_size)
            no_improve_count += 1
            continue

        # Sort candidates by gain (high to low)
        candidates.sort(key=lambda x: -x[1])
        add_count = min(remove_count, len(candidates))
        chosen = [x[0] for x in candidates[:add_count]]

        # Add chosen subsets
        new_solution = temp_solution.copy()
        for idx in chosen:
            new_solution.append(idx)
            update_coverage(add_idx=idx)

        # Check if new solution is valid
        uncovered = get_uncovered_elements()
        if not uncovered and len(new_solution) < current_cost:
            current_solution = new_solution
            current_cost = len(new_solution)
            if current_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = current_cost
                trace.append((time.time() - start_time, best_cost))
                no_improve_count = 0
                swap_size = 1  # Reset swap size
                print(f"Improved solution: cost={current_cost}")
        else:
            # Revert changes
            for idx in chosen:
                update_coverage(remove_idx=idx)
            for idx in remove_subsets:
                update_coverage(add_idx=idx)
            no_improve_count += 1
            swap_size = min(swap_size + 1, max_swap_size)

        # Periodic greedy re-optimization
        if no_improve_count % 10 == 0 and no_improve_count > 0:
            # Remove redundant subsets
            temp_solution = current_solution.copy()
            random.shuffle(temp_solution)
            for idx in temp_solution[:]:
                update_coverage(remove_idx=idx)
                # For each subset, removes it and checks if the universe is still covered. If covered, keeps it removed; otherwise, re-adds it.
                if not get_uncovered_elements():
                    temp_solution.remove(idx)
                else:
                    update_coverage(add_idx=idx)
            if len(temp_solution) < current_cost:
                current_solution = temp_solution
                current_cost = len(current_solution)
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
                    trace.append((time.time() - start_time, best_cost))
                    no_improve_count = 0
                    swap_size = 1
                    print(f"Greedy re-optimization: cost={current_cost}")

        if no_improve_count >= no_improve_limit:
            # Perturb solution by restarting from greedy with small random changes by removing 1,2 element
            temp_solution, _ = greedy_approximation(instance)
            if len(temp_solution) > 2:
                remove_count = random.randint(1, 2)
                temp_solution = random.sample(temp_solution, len(temp_solution) - remove_count)
                uncovered = get_uncovered_elements()
                for j in random.sample(range(1, instance.m + 1), instance.m):
                    if j not in temp_solution and subset_coverages[j - 1] & uncovered:
                        temp_solution.append(j)
                        update_coverage(add_idx=j)
                        uncovered = get_uncovered_elements()
                        if not uncovered:
                            break
                if len(temp_solution) < current_cost and not get_uncovered_elements():
                    current_solution = temp_solution
                    current_cost = len(current_solution)
                    no_improve_count = 0
                    swap_size = 1
                    print(f"Perturbed solution: cost={current_cost}")

        if time.time() - start_time > cutoff - 1:
            print("Approaching cutoff time, stopping search.")
            break

    print(f"Best solution: cost={best_cost}")
    print(f"{time.time() - start_time:.2f} seconds elapsed")
    return best_solution, best_cost, trace