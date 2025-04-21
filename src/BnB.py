#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[13]:


import os
import time
from queue import PriorityQueue

# Set paths for your Mac
data_dir = "/Users/xiaofengwu/Desktop/Project/data"
output_dir = "/Users/xiaofengwu/Desktop/Project/output"
os.makedirs(output_dir, exist_ok=True)

def read_input(filename):
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


# In[15]:


cutoff = 900  # 15 minutes
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

        sol_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.sol")
        with open(sol_path, 'w') as f:
            f.write(f"{cost}\n")
            f.write(' '.join(map(str, sorted(solution))) + '\n')

        trace_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.trace")
        with open(trace_path, 'w') as f:
            for t, val in trace:
                f.write(f"{t:.2f} {val}\n")

        print(f"✔ Finished {filename} in {elapsed_time:.2f} seconds\n")


# In[39]:


import pandas as pd
import os

def read_output_file(filepath):
    with open(filepath, 'r') as f:
        return int(f.readline().strip())

def read_solution_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return int(lines[0].strip())

def read_trace_time(trace_path):
    try:
        with open(trace_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        if len(lines) >= 2:
            # BnB improved greedy — return time of last update
            last_line = lines[-1]
            return round(float(last_line.split()[0]), 6), False
        elif len(lines) == 1:
            # Only greedy was used
            return 0.0, True
    except:
        pass
    return None, None  # If something goes wrong

results = []

for filename in os.listdir(data_dir):
    if filename.endswith(".out") and (filename.startswith("small") or filename.startswith("large")):
        instance = filename[:-4]
        out_path = os.path.join(data_dir, filename)
        sol_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.sol")
        trace_path = os.path.join(output_dir, f"{instance}_{alg_name}_{cutoff}.trace")

        if not os.path.exists(sol_path):
            continue

        try:
            opt = read_output_file(out_path)
            collection_size = read_solution_file(sol_path)
            rel_err = round((collection_size - opt) / opt, 4)
            time_to_best, greedy_only = read_trace_time(trace_path)

            results.append({
                "Dataset": instance,
                "collection size": collection_size,
                "OPT": opt,
                "RelErr": rel_err,
                "Time to Best (s)": time_to_best if time_to_best is not None else "N/A",
                "Used Greedy Only": greedy_only
            })
        except:
            continue

# Sort results nicely
def sort_key(r):
    prefix = r["Dataset"][:5]
    num = int(''.join(filter(str.isdigit, r["Dataset"])))
    return (prefix, num)

results = sorted(results, key=sort_key)
df = pd.DataFrame(results)

# Format time for display
df["Time to Best (s)"] = df["Time to Best (s)"].map(lambda x: f"{x:.6f}" if isinstance(x, float) else x)

display(df)

# Save to CSV
df.to_csv(os.path.join(output_dir, "bnb_results_summary.csv"), index=False)


# In[ ]:




