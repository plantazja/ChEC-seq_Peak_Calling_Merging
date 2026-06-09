import sys, os
import argparse
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from collections import defaultdict

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("-M", nargs="+",
                   help="List of bed files")
    p.add_argument("--output", type=str,
                   help="Output png file")
    return(p.parse_args())

def plot_peaks(samples, output):
    # Get peaks count
    samples_dict = defaultdict()
    for s in samples:
        df = pd.read_csv(s, sep='\t', header=None)
        s_name = os.path.basename(s)
        s_name = s_name.split(".")[0]
        samples_dict[s_name] = df.shape[0]
    
    # Plot
    ax = sns.barplot(x=list(samples_dict.keys()),
                    y= list(samples_dict.values()))
    ax.bar_label(ax.containers[0])
    ax.set(
        xlabel="",
        ylabel="Peaks count"
    )
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    try:
        args = cmdline_args()
        plot_peaks(args.M, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)