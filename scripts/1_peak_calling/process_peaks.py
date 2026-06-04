import sys, os
import argparse
import pandas as pd

chr_lengths = {
                'chrI': 230218,
                'chrII': 813184,
                'chrIII': 316620,
                'chrIV': 1531933,
                'chrV': 576874,
                'chrVI': 270161,
                'chrVII': 1090940,
                'chrVIII': 562643,
                'chrIX': 439888,
                'chrX': 745751,
                'chrXI': 666816,
                'chrXII': 1078177,
                'chrXIII': 924431,
                'chrXIV': 784333,
                'chrXV': 1091291,
                'chrXVI': 948066,
                'chrMT': 85779
            }

def cmdline_args():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("--input", type=str,
                   help="Input bed file")
    p.add_argument("--out_dir", type=str,
                   help="Output directory")
    p.add_argument("-t", type=int,
                   help="Telomer length to cut on both end of chromosomes")
    return(p.parse_args())

def process_bed(in_file, out_dir, telomer_length):
    '''
    Parsing raw .bed output from HOMER to new .bed file with 'center' column.
    '''
    bed_df = pd.read_csv(in_file, sep='\t', header=None, usecols=[1,2,3,11], names=['chr','start','end','p-value vs Control'], comment='#')
    bed_df['start'] = bed_df['start'].astype(int)
    bed_df['end'] = bed_df['end'].astype(int)
    peak_size = bed_df['end'] - bed_df['start']
    bed_df['center'] = bed_df['start'] + peak_size / 2
    bed_df['center'] = bed_df['center'].astype(int)
    chroms = list(chr_lengths.keys())
    bed_df.chr = pd.Categorical(values=bed_df.chr, categories=chroms, ordered=True)
    bed_df.sort_values(['chr', 'center'], inplace=True)

    # Remove peaks that mapped on rDNA locus on chrXII
    bed_df = bed_df.drop(bed_df[(bed_df['chr'] == 'chrXII') &
                                (bed_df['end'] >= 451000) &
                                (bed_df['start'] <= 469000)].index)
    
    # Cut telomers from each chromosome
    if telomer_length > 0:
    filtered_dfs = []
    for chr_n, chr_l in chr_lengths.items():
        chr_df = bed_df[bed_df['chr'] == chr_n]
        chr_df = chr_df[(chr_df['start'] > telomer_length) &
                        (chr_df['end'] < chr_l - telomer_length)]
        filtered_dfs.append(chr_df)
    
    if filtered_dfs:
        bed_df = pd.concat(filtered_dfs, ignore_index=True)
    else:
        # If all chromosomes filtered out, create empty dataframe
        bed_df = pd.DataFrame(columns=bed_df.columns)
    
    # Save clean bed file
    file_name = os.path.basename(in_file)
    out_file = os.path.join(out_dir, file_name)
    bed_df[['chr', 'start', 'end', 'center', 'p-value vs Control']].to_csv(out_file, header=False, index=False, sep='\t')

if __name__ == '__main__':
    try:
        args = cmdline_args()
        process_bed(args.input, args.out_dir, args.t)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)