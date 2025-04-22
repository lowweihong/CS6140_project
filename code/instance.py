from typing import List, Set

class SetCoverInstance:
    def __init__(self, n: int, m: int, subsets: List[Set[int]]):
        """
        Initialize Set Cover Instance
        Args:
            n: Number of elements in universe
            m: Number of subsets
            subsets: List of sets containing elements
        """
        self.n = n  # number of elements
        self.m = m  # number of subsets
        self.subsets = subsets
        self.universe = set(range(1, n + 1))

def read_instance(filename: str) -> SetCoverInstance:
    """
    Read Set Cover instance from file.
    File format:
    First line: n m (space-separated integers)
    Next m lines: size followed by elements in the subset
    """
    with open(filename, 'r') as f:
        # Read first line containing n and m
        n, m = map(int, f.readline().split())
        
        # Read m subsets
        subsets = []
        for _ in range(m):
            # Read line and parse numbers
            line = list(map(int, f.readline().split()))
            subset_size = line[0]
            # Create set from elements (excluding the size)
            subset = set(line[1:subset_size+1])
            subsets.append(subset)
            
        return SetCoverInstance(n, m, subsets)
