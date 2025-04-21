import os
import time
from queue import PriorityQueue

# Change these if running on a different machine or directory
data_dir = os.path.join("..", "data")      # ../data
output_dir = os.path.join("..", "output")  # ../output
os.makedirs(output_dir, exist_ok=True)

def read_input(filename):
    """Reads a Set Cover instance from a file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].strip().split())
    sets = []
    for line in lines[1:]:
        parts = list(map(int, line.strip().split()))
        sets.append(set(parts[1:]))
    universe = set(range(1, n + 1))
    return universe, sets

def greedy_set_cover(universe, sets):
    """Greedy algorithm to approximate set cover."""
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
    """Branch and Bound algorithm for Set Cover."""
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

        # Include branch
        new_selected = selected + [i]
        new_covered = covered | sets[i]
        gain = len(sets[i] & (universe - covered))
        new_lb = len(new_selected)
        priority = new_lb - gain * 0.01  # favor higher gain

        if new_lb < best_cost and new_covered != covered and queue.qsize() < MAX_QUEUE:
            queue.put((priority, new_selected, new_covered, remaining))

        # Exclude branch
        if lb < best_cost and queue.qsize() < MAX_QUEUE:
            queue.put((lb, selected, covered, remaining))

    return best_solution, best_cost, trace

# Run the algorithm for all .in files in the data directory
if __name__ == "__main__":
    cutoff = 900  # seconds
    alg_name = "BnB"

    for filename in os.listdir(data_dir):
        if filename.endswith(".in"):
            instance = filename[:-3]
            input_path = os.path.join(data_dir, filename)
            print(f"Processing {filename} at {time.strftime('%H:%M:%S')}...")

            universe, sets = read_input(input_path)
            start_time = time.time()
            solution, cost, trace = branch_and_bound(universe, sets, cutoff)
            elapsed_time = time.time() - start_time

            # Write .sol file
            sol_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.sol")
            with open(sol_path, 'w') as f:
                f.write(f"{cost}\n")
                f.write(' '.join(map(str, sorted(solution))) + '\n')

            # Write .trace file
            trace_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.trace")
            with open(trace_path, 'w') as f:
                for t, val in trace:
                    f.write(f"{t:.2f} {val}\n")

            print(f"✔ Finished {filename} in {elapsed_time:.2f} seconds\n")
