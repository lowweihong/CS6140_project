# Set Cover Problem Solver

This Python program solves the Set Cover Problem using various algorithms: 
1. Branch and Bound (BnB): Branch and bound algorithm.
2. Approximation (Approx): Greedy approximation algorithm.
3. Local Search 1 (LS1): Hill Climbing algorithm.
4. Local Search 2 (LS2): Simulated Annealing algorithm.

## Usage
From the current directory (`code/`), run the program from the command line with the following command:

```bash
python main.py -inst <instance_file> -alg <algorithm> -time <cutoff_time> -seed <random_seed>
```
* After running this, you may find the resulting `.sol` and `.trace` file on the same directory as the main.py script.


## Project Structure


Project structure:
```
├──code/
|    │── main.py                                    # Main file to run all algorithms
|    │── approximation.py                           # File for greedy approximation algorithm
|    ├── bnb.py                                     # File for branch and bound algorithm 
|    ├── localsearch_sa.py                          # File for local search for Simulated Annealing algorithm
|    ├── localsearch_hc.py                          # File for local search for Hill Climbing algorithm
|    ├── instance.py                                # File to create set cover instance
|    ├── evaluate.py                                # File to generate QRTD, SQD plots and boxplots
└──output/                                          # Directory containing all the generated .sol and .trace files
     ├── *.sol
     └── *.trace

```