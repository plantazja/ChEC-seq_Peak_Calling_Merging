## Work in progress.
---

This project contains a Snakemake pipeline for seamless peak calling and merging of peaks from three replicates for multiple samples, as well as notebooks for downstream analysis, such as comparing peak locations and signal intensities between samples.

### Peak calling 
The pipeline expects `.bam` files with a format `Strain_rep`.

Recommended format:
`RDY000_phase_treatment_time_conct_rep`, where:

- **phase**: `"as"`, `"G1"`, `"S"`, `"G2"`
- **treatment**: `"unTR"`, `"DMSO"`, `"IAA"`
- **time**: `"nT"`, `"00"`, `"05"`...
- **concentration**: `"nC"`, `"01"`, `"05"`, `"10"`...
- **rep**: `"A"`, `"B"`, `"C"` - suffix required

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

## Instructions how to run on Slurm managed HPC
#### a) Download version controlled repository
```bash
git clone https://github.com/plantazja/ChEC-seq_Peak_Calling_Merging
cd ChEC-seq_Peak_Calling_Merging
```
#### b) Load modules
```bash
ml homer
module load slurm python/3.10 python/3.10 pandas/2.2.3 numpy/1.22.3 matplotlib/3.7.1 seaborn/0.12.2
```
#### c) Modify config file - change path to ChEC-Seq_Analysis project
```bash
nano config/config.yml
```
#### d) Dry Run
```bash
snakemake -npr
```
#### e) Run on HPC
```bash
sbatch --wrap="snakemake -j 20 --use-envmodules --rerun-incomplete --latency-wait 300 --cluster-config config/cluster_config.yml --cluster 'sbatch -A {cluster.account} -p {cluster.partition} --cpus-per-task {cluster.cpus-per-task}  -t {cluster.time} --mem {cluster.mem} --output {cluster.output}'"
```