############################################
###### Greedy algorithm approximation#######
############################################

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

