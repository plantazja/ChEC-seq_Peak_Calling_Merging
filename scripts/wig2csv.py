import pandas as pd
import numpy as np
import sys, os
import argparse
import csv

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("--bed", type=str,
                   help="Path to bed file")
    p.add_argument("--wig", type=str,
                   help="Path to of wig file")
    p.add_argument("--output", type=str,
                   help="Path to csv file")
    return(p.parse_args())

CHROMS = ['chrI','chrII','chrIII','chrIV','chrV','chrVI','chrVII','chrVIII',
          'chrIX','chrX','chrXI','chrXII','chrXIII','chrXIV','chrXV','chrXVI']

def get_signals(bed_path, wig_path):
    # Read BED file
    bed = pd.read_csv(bed_path, header=None, sep="\t")
    
    # Build IntervalTree for each chromosome
    chrom_trees = {chrom: IntervalTree() for chrom in CHROMS}
    
    # Store original BED indices and positions for later mapping
    bed_info = []  # list of (chrom, start, end, original_index)
    
    for idx, row in bed.iterrows():
        chrom, start, end = row[0], int(row[1]), int(row[2])
        chrom_trees[chrom].addi(start, (end+1), idx)
        bed_info.append((chrom, start, (end+1), idx))
    
    # Initialize signal storage
    signals = []
    for _, row in bed.iterrows():
        start, end = int(row[1]), int(row[2])
        signals.append({pos: 0 for pos in range(start, end + 1)})
    
    chunk_size = 100000
    current_chrom = None
    
    for chunk in pd.read_csv(wig_path, chunksize=chunk_size, sep=' ', header=0):
        for row in chunk.itertuples(index=False):
            # Parse variableStep line
            if row[0] == "variableStep":
                current_chrom = row[1].split("=")[1]
                print(f"Processing chromosome {current_chrom}..")
                continue
            
            # Skip if no chromosome set
            if current_chrom is None:
                continue
            
            pos, sig = int(row[0]), float(row[1])
            
            # Query interval tree for overlapping regions at this position
            # Using a tiny interval around pos for exact position matching
            overlapping = chrom_trees[current_chrom].overlap(pos, pos + 1)
            
            for interval in overlapping:
                idx = interval.data  # Original BED row index
                if pos in signals[idx]:
                    signals[idx][pos] = sig
    
    # Convert to DataFrame
    signals_lst = [list(s.values()) for s in signals]
    df = pd.DataFrame(signals_lst).T
    return df

if __name__ == '__main__':
    args = cmdline_args()
    df = get_signals(args.bed, args.wig)
    df.to_csv(args.output, sep='\t', header=False, index=False)