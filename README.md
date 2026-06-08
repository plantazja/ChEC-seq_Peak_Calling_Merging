## Work in progress.
---

This project contains a Snakemake pipeline for seamless peak calling and merging of peaks from three replicates for multiple samples, as well as notebooks for downstream analysis, such as comparing peak locations and signal intensities between samples.

### Peak calling 
The pipeline expects `.bam` files with a specific name format: `RDY000_phase_treatment_time_conct_rep`, where:

- **phase**: `"as"`, `"G1"`, `"S"`, `"G2"`
- **treatment**: `"unTR"`, `"DMSO"`, `"IAA"`
- **time**: `"nT"`, `"00"`, `"05"`...
- **concentration**: `"nC"`, `"01"`, `"05"`, `"10"`...
- **rep**: `"A"`, `"B"`, `"C"`

The pipeline works with exactly three replicates per experiment and merges their peaks into a single `.bed` output file.

## Pipeline steps:

### a) BAM to SAM Conversion
-- **Input**: .bam files

-- **Output**: 'results/sam'

-- **Tool**: SAMtools

### b) Peak Calling with HOMER
**Command**
```bash
    findPeaks $tag_dir/$name -style factor -size 150 -i $control -o auto -C 0 -L 3 -F 3 2
```
-L 3 and -F 3 parameters less restrictive to "weaker" peaks.
Fixed size of peaks gives higher reproducibility across replicates.

-- **Output**: 'results/homer_peaks'

-- **Tool**: HOMER

### c) HOMER .bed processing
-- **Output**: 'results/homer_peaks_processed'
Removes unnecessary columns
Filters out peaks mapping to rDNA locus on chromosome XII (coordinates: 451,000 - 469,000)

### d) Peaks merging across 3 replicates
**Merging algorithm:** 
1) Identifies overlapping intervals between any replicates
2) Defines new merged interval: center is mean of centers of overlapping intervals, start is position is -75 bp from center and end is position +75 from center.

Filter out peaks in telomere region (1000 bp from start and end of each chromosome)

-- **Output**: 'results/merged_peaks' 