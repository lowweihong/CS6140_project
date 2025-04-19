import glob
import os
import csv
from decimal import Decimal, ROUND_HALF_UP
import matplotlib.pyplot as plt
import numpy as np

def read_input(filename,type=None):
    """
    Read the solution from trace file
    
    Args:
        filename: Path to trace file
        
    Returns:
        time
        value:collection size
    """
    if type == "OUT":
        with open(filename, 'r') as f:
            OPT = (list(f)[0])      
        return float(OPT)
        
    else:
        with open(filename, 'r') as f:
            elapsed, best_cost = (list(f)[-1]).split()

        return float(elapsed),float(best_cost)

def write_solution(filename, dict):
    """
    Write solution to file
    
    Args:
        filename: Path to output file
        dict
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['Dataset', 'Time', 'Value', 'RelErr']
        writer.writerow(header)
        
        for key, values in dict.items():
            row = [key] + values
            writer.writerow(row)

def round_(value):
    return Decimal(value).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)


def plot_qrtd(instance_name, qrtd_data, colors=None):
    """
    Plot QRTDs for different q* values.
    
    Parameters:
    - instance_name: Name of the problem instance
    - qrtd_data: Dictionary with q* as keys and list of (time, fraction) tuples as values
    - colors: Optional dictionary mapping q* values to colors
    """
    plt.figure(figsize=(10, 6))    
    
    if not colors:
        colors = {
            0.0: 'red',
            0.2: 'orange',
            0.4: 'green',
            0.6: 'blue',
            0.8: 'purple',
            1.0: 'black'
        }
    
    for q in sorted(qrtd_data.keys()):
        times, fractions = zip(*qrtd_data[q])
        plt.plot(times, fractions, label=f'q* = {q}%', color=colors.get(q))
    
    plt.title(f'Qualified Runtime Distribution (QRTD) for {instance_name}')
    plt.xlabel('Runtime (seconds)')
    plt.ylabel('Fraction of runs solved')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'qrtd_{instance_name}.png', dpi=300)
    plt.show()

def plot_sqd(problem_name, sqd_data, colors=None):
    """Plot SQDs for different time points"""
    if not sqd_data:
        print(f"No data to plot for {problem_name}")
        return
    
    plt.figure(figsize=(10, 6))
    
    if not colors:        
        cmap = plt.cm.viridis
        colors = {t: cmap(i/len(sqd_data)) for i, t in enumerate(sorted(sqd_data.keys()))}
    
    for t in sorted(sqd_data.keys()):
        qualities, fractions = zip(*sqd_data[t])
        plt.plot(qualities, fractions, label=f't = {t:.2f}s', color=colors.get(t, 'gray'), linewidth=2)
    
    plt.title(f'Solution Quality Distribution (SQD) for {problem_name}')
    plt.xlabel('Solution quality (% from optimal)')
    plt.ylabel('Fraction of runs')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.ylim(0, 1.05)  # Set y-axis limit from 0 to just above 1
    plt.tight_layout()
    plt.savefig(f'sqd_{problem_name}.png', dpi=300)
    plt.show()

def boxplot_(boxplot_dic):
    plt.boxplot(boxplot_dic.values(), tick_labels=boxplot_dic.keys())
    plt.title(f"Execution Time Distribution for large 1 and large10")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.savefig(f'boxplot_large1_large10.png', dpi=300)
    plt.show()

def main():

    from collections import defaultdict
    trace_dic=defaultdict(list)
    opt_dic = defaultdict(int)
    
    
    tracenames="*.trace"
    inst_trace = glob.glob(tracenames)
    for file_path in inst_trace:
        elapsed, best_cost = read_input(file_path)
        instance_name = os.path.splitext(os.path.basename(file_path))[0] 
        instance_name = instance_name.split("_")[0]        
        trace_dic[instance_name].append([elapsed, best_cost])
    
    plot_dic=trace_dic.copy()

    for key, value in trace_dic.items(): 
        avg = [sum(x) / len(x) for x in zip(*value)]
        trace_dic[key] =avg   

    optnames="*.out"
    inst_opt = glob.glob(optnames)    
    for file_path in inst_opt:
        opt=read_input(file_path,"OUT")
        instance_name = os.path.splitext(os.path.basename(file_path))[0] 
        opt_dic[instance_name] = opt
        RelErr=trace_dic[instance_name][1]/opt-1
        trace_dic[instance_name].append(RelErr)      

    trace_dic = dict(sorted(trace_dic.items(), key=lambda item: (item[0], item[1][0],item[1][0])))

    write_solution("compre_table", trace_dic)


    ##### Boxplot ###

    plot_list=['large1','large10']    
    boxplot_dic = {k: [item[0] for item in v] for k, v in plot_dic.items() if k in plot_list}
    boxplot_(boxplot_dic)    
    
    ### # Calculate QRTDs ###
    q_stars = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for key in plot_list:
        times = [entry[0] for entry in plot_dic[key]]
        values = [entry[1] for entry in plot_dic[key]]
        opt=opt_dic[key]        
         
        sorted_indices = np.argsort(times)
        sorted_times = np.array(times)[sorted_indices]
        sorted_values = np.array(values)[sorted_indices]             
        num_runs=len(plot_dic[key])
        max_time=max(times)        
                
        q_thresholds = {q: opt + (q/100)* opt for q in q_stars}        
        results = {q: [] for q in q_stars} 
        time_points = np.linspace(0, max_time, 100)
        
        for q in q_stars:           
            threshold = q_thresholds[q]            
            fractions = []

            for time_point in time_points:                
                count = 0
                idx = np.searchsorted(sorted_times, time_point, side='right')

                if idx > 0: 
                    for i in range(idx):                    
                        if sorted_values[i] <= threshold: 
                            count += 1
                fraction = count / num_runs 
                                            
                fractions.append(fraction)          
            
            results[q] = list(zip(time_points, fractions))                   

        plot_qrtd(key, results, colors=None)


        # Calculate SQD
        sqd_time_points = [max_time * i / 10 for i in range(1, 11)]  
        sqd_results = {t: [] for t in sqd_time_points}
        
        for time_point in sqd_time_points:
            q_values = np.linspace(0, 10, 51)  
            fractions = []
            
            for q in q_values:
                threshold = opt + (q/100) * opt
                idx = np.searchsorted(sorted_times, time_point, side='right')
                count = 0
                
                if idx > 0:
                    for i in range(idx):                    
                        if sorted_values[i] <= threshold:
                            count += 1
                
                fraction = count / num_runs
                fractions.append(fraction)
            
            sqd_results[time_point] = list(zip(q_values, fractions))
        
        plot_sqd(key, sqd_results)   
        

if __name__ == "__main__":
    main()






    