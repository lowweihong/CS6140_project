import os
import csv
from instance import read_instance


def read_to_subset(file):
    """
    Reads a set cover instance file and extracts subset information.

    Parameters:
    -----------
    file : str
        Path to the instance file to be read

    Returns:
    --------
    tuple
        A tuple containing three elements:
        - subsets (list): List of sets, where each set contains the elements
        - num_elements (int): Total number of elements in the universe
        - num_subsets (int): Total number of subsets

    """
    instance = read_instance(file)
    universe = instance.universe.copy()
    subsets = instance.subsets.copy()
    num_elements = len(universe)
    num_subsets = len(subsets)
    return subsets, num_elements, num_subsets

def analyze_set_cover_sparsity(subsets, num_elements, num_subsets):
    """
    Analyze the sparsity of a set cover instance.
    
    Parameters:
    - subsets: List of lists, where each inner list contains the elements in a subset.
    - num_elements: Total number of elements (e.g., 50).
    - num_subsets: Total number of subsets (e.g., 500).
    
    Returns:
    - A dictionary with sparsity metrics and an assessment of whether the instance is sparse.
    """
    # Initialize element frequency dictionary
    element_frequency = {i: 0 for i in range(1, num_elements + 1)}
    
    # Count subset sizes and element frequencies
    subset_sizes = []
    total_entries = 0  # Total number of element-subset pairs (1s in incidence matrix)
    
    for subset in subsets:
        size = len(subset)  # Number of elements in the subset
        subset_sizes.append(size)
        total_entries += size
        # Update frequency for each element in the subset
        for element in subset:
            if element in element_frequency:
                element_frequency[element] += 1
    print(element_frequency)
    
    # Compute metrics
    avg_subset_size = sum(subset_sizes) / len(subset_sizes) if subset_sizes else 0
    avg_element_frequency = sum(element_frequency.values()) / len(element_frequency)
    
    # Compute incidence matrix density
    total_possible_entries = num_elements * num_subsets
    density = total_entries / total_possible_entries if total_possible_entries > 0 else 0
    
    # Determine sparsity
    # - Low element frequency (e.g., <10% of subsets, or <50 for 500 subsets)
    # - Low subset size (e.g., <10% of elements, or <5 for 50 elements)
    # - Low density (e.g., <5%)
    sparsity_thresholds = {
        'max_element_frequency_ratio': 0.10,  # Element frequency < 10% of subsets
        'max_subset_size_ratio': 0.10,       # Subset size < 10% of elements
        'max_density': 0.05                  # Density < 5%
    }
    
    is_sparse = (
        avg_element_frequency < sparsity_thresholds['max_element_frequency_ratio'] * num_subsets and
        avg_subset_size < sparsity_thresholds['max_subset_size_ratio'] * num_elements and
        density < sparsity_thresholds['max_density']
    )
    
    # Prepare results
    results = {
        'num_elements': num_elements,
        'num_subsets': num_subsets,
        'avg_subset_size': avg_subset_size,
        'avg_element_frequency': avg_element_frequency,
        'density': density,
        'min_element_frequency': min(element_frequency.values()),
        'max_element_frequency': max(element_frequency.values()),
        'is_sparse': is_sparse
    }
    
    return results


def generate_sparsity_csv(data_directory, output_csv):
    """
    Loop through instance files in the data directory, analyze sparsity, and write results to a CSV.
    
    Parameters:
    - data_directory: Path to the directory containing instance files.
    - output_csv: Path to the output CSV file.
    """
    # List of instance files to process
    instance_files = [f'large{i}.in' for i in range(1, 12)] + [f'small{i}.in' for i in range(1, 19)]
    
    # CSV column headers
    headers = [
        'Instance', 'Number of Elements', 'Number of Subsets', 'Average Subset Size',
        'Average Element Frequency', 'Incidence Matrix Density', 'Min Element Frequency',
        'Max Element Frequency', 'Is Sparse'
    ]
    
    # Collect results
    results = []
    
    for instance in instance_files:
        file_path = os.path.join(data_directory, instance)
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found, skipping.")
            continue
        
        try:
            # Parse the instance
            subsets, num_elements, num_subsets = read_to_subset(file_path)
            
            # Analyze sparsity
            sparsity_results = analyze_set_cover_sparsity(subsets, num_elements, num_subsets)
            # sparsity_results = analyze_set_cover_sparsity(subsets, num_elements, num_subsets)
            
            # Prepare row for CSV
            row = {
                'Instance': instance,
                'Number of Elements': sparsity_results['num_elements'],
                'Number of Subsets': sparsity_results['num_subsets'],
                'Average Subset Size': round(sparsity_results['avg_subset_size'], 2),
                'Average Element Frequency': round(sparsity_results['avg_element_frequency'], 2),
                'Incidence Matrix Density': round(sparsity_results['density'], 4),
                'Min Element Frequency': sparsity_results['min_element_frequency'],
                'Max Element Frequency': sparsity_results['max_element_frequency'],
                'Is Sparse': sparsity_results['is_sparse']
            }
            results.append(row)
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    # Write results to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"Sparsity analysis completed. Results written to {output_csv}")

if __name__ == "__main__":
    data_directory = 'data'  # Directory containing instance files
    output_csv = 'sparsity_analysis.csv'  # Output CSV file
    generate_sparsity_csv(data_directory, output_csv)
