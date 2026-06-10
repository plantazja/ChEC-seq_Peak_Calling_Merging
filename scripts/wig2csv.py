import pandas as pd
import numpy as np
import sys, os
import csv

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("--bed", nargs="+",
                   help="List of bed files")
    p.add_argument("--wig", nargs="+",
                   help="List of wig files")
    p.add_argument("--output", nargs="+",
                   help="List of csv files")
    return(p.parse_args())

def get_signals(bed_path, wig_path):
    bed = pd.read_csv(bed_path, header=None, sep="\t")

    chunk_size = 100000  # Adjust based on your memory
    i = 0
    cur_start = int(bed.iloc[i,1])
    cur_end = int(bed.iloc[i,2])
    cur_chr = bed.iloc[i,0]

    signals = []
    cur_signals = {i:0 for i in range(cur_start, (cur_end+ 1))}

    for chunk in pd.read_csv(wig_path, chunksize=chunk_size, sep=' ', header=0):
        for row in chunk.itertuples(index=False):
            # Situation 1: row with chr information
            if row[0] == "variableStep":
                chr_inf = row[1]
                chr = chr_inf.split("=")[1]
                continue

            pos, sig = int(row[0]), float(row[1])

            # Situation 2: Position inside peak coordinates - append signal value
            if cur_start <= pos <= cur_end and chr == cur_chr:
                cur_signals[pos] = sig

            # Situation 3: Leaving peak - add new column to output df and init new peak start and end
            elif pos > cur_end and chr == cur_chr:
                signals.append(cur_signals)
                i += 1
                if i >= len(bed):
                    break

                cur_start = bed.iloc[i,1]
                cur_end = bed.iloc[i,2]
                cur_chr = bed.iloc[i,0]
                cur_signals = {i:0 for i in range(cur_start, (cur_end+ 1))}
                
            # Situation 4: Position is less then current start - ignore
    signals_lst = [s.values() for s in signals]
    df = pd.DataFrame(signals_lst)
    return df.T

if __name__ == '__main__':
    args = cmdline_args()
    df = get_signals(args.bed, args.wig)
    df.to_csv(args.output, sep='\t', header=False, index=False)