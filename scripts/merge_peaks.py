import argparse
import numpy as np
import pandas as pd
import sys

CHROMS = ['chrI','chrII','chrIII','chrIV','chrV','chrVI','chrVII','chrVIII','chrIX','chrX','chrXI','chrXII','chrXIII','chrXIV','chrXV','chrXVI']

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("-A", type=str,
                   help="Input bed file for replicate A")
    p.add_argument("-B", type=str,
                   help="Input bed file for replicate B")
    p.add_argument("-C", type=str,
                   help="Input bed file for replicate C")
    p.add_argument("--output", type=str,
                   help="Path to new merged bed file")
    return(p.parse_args())

def load_data(path_A, path_B, path_C) -> list:
    replicates = []
    for rep_path in [path_A, path_B, path_C]:
        df = pd.read_csv(rep_path, usecols=[0,1,2,3], sep='\t', header=None)
        df.columns = ['chr', 'start', 'end', 'center']
        df['start'] = df['start'].astype(int)
        df['end'] = df['end'].astype(int)
        df['center'] = df['center'].astype(float)
        replicates.append(df)
    return replicates

def merge_replicates(replicates, outpath) -> pd.DataFrame:
    '''
    Algorithm to find overlapping peaks in at least 2 out of 3 replicates.
    Works for 3 samples only.
    '''
    merged = {'chr': [], 'start': [], 'end': [], 'center': []}

    for chrom in CHROMS:
        # Collect all intervals with their replicate ID
        intervals = []
        for rep, rep_df in enumerate(replicates):
            rep_chrom = rep_df[rep_df['chr'] == chrom]
            for _, row in rep_chrom.iterrows():
                intervals.append((row['start'], row['end'], row['center'], rep))
        if not intervals:
            print(f'Warning: chromosome {chrom} has no peaks for all replicates.')
            continue

        #############    Merging algorithm    ############
        # Sort from start position
        intervals.sort(key=lambda x: x[0])
        # Init start and end for first interval
        current_start = None
        current_end = None
        active_reps = set()

        for start, end, center, rep in intervals:
            # Init start and end
            if current_start is None and current_end is None:
                current_start = start
                current_end = end
                active_reps.add((center, rep))

            # Overlap, new start inside, new end outside
            elif start < current_end and end >= current_end: 
                # Change only start
                current_start = start
                active_reps.add((center, rep))

            # Overlap, new interval is fully inside 'current' interval
            elif start >= current_start and end <= current_end: 
                current_start = start
                current_end = end
                active_reps.add((center,rep))
            
            # Overlap, start outside, end inside
            elif start <= current_start and end < current_end: 
                # Change only end
                current_end = end
                active_reps.add((center,rep))

            elif start >= current_end: #leaving overlapping
                # We want record only overlapped regions
                if len(active_reps) >= 2 and current_start is not None:
                    center_mean = int(np.mean([rep[0] for rep in active_reps]))
                    # Found an overlap region
                    # Record new overlap region using mean of centers of overlapped intervals
                    # Start is -75 bp from new center and end is +75 bp.
                    merged['chr'].append(chrom)
                    merged['start'].append(int(center_mean - 75))
                    merged['end'].append(int(center_mean + 75))
                    merged['center'].append(center_mean)

                # Reset for the new interval
                current_start = start
                current_end = end
                active_reps = {(center, rep)}
        
        # Check for the last interval
        if len(active_reps) >= 2 and current_start is not None:
            center_mean = np.mean([rep[0] for rep in active_reps])
            merged['chr'].append(chrom)
            merged['start'].append(int(center_mean - 75))
            merged['end'].append(int(center_mean + 75))
            merged['center'].append(center_mean)
    
    merged = pd.DataFrame(merged)
    merged.to_csv(outpath, sep='\t', index=False, header=False)

if __name__ == '__main__':
    try:
        args = cmdline_args()
        replicates = load_data(args.A, args.B, args.C)
        merge_replicates(replicates, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)