import sys, os
import argparse
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from collections import defaultdict

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("--csvs", nargs="+",
                   help="List of csv files")
    p.add_argument("--output", type=str,
                   help="Output png file")
    return(p.parse_args())

def plot_peaks(samples, output):
    # Get peaks count
    samples_dict = defaultdict(list)
    for s in samples:
        df = pd.read_csv(s, sep='\t', header=None, index_col=False)
        s_name = os.path.basename(s)
        s_name = s_name.split(".")[0]
        samples_dict[s_name] = df.sum(axis=0)
    
    # Plot violins
    ax = sns.violinplot(data=samples_dict)
    ax.set(
        xlabel="",
        ylabel="Signal"
    )
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    args = cmdline_args()
    plot_peaks(args.csvs, args.output)