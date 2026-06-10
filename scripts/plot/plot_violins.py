import sys, os
import argparse
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import numpy as np

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("--csvs", nargs="+",
                   help="List of csv files")
    p.add_argument("--output", type=str,
                   help="Output png file")
    return(p.parse_args())

def plot_peaks(samples, output):
    # Dictionary with sample name as key, list of peak sums as values
    samples_dict = {}
    
    for s in samples:
        df = pd.read_csv(s, sep='\t', header=None, index_col=False)

        s_name = os.path.basename(s)
        s_name = s_name.split(".")[0]
        
        # Calculate sum for each column (peak)
        peak_sums = df.sum(axis=0).values 
        
        # Store in dictionary as list
        samples_dict[s_name] = peak_sums.tolist() 
    
    plot_data = []
    for sample_name, peak_sums in samples_dict.items():
        for peak_sum in peak_sums:
            plot_data.append({
                'sample': sample_name,
                'signal_sum': peak_sum
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Plot violin
    plt.figure(figsize=(12, 6))
    ax = sns.violinplot(data=plot_df, x='sample', y='signal_sum')
    ax.set(
        xlabel="",
        ylabel="Total Signal per Peak"
    )
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    args = cmdline_args()
    plot_peaks(args.csvs, args.output)