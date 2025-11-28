#!/bin/bash/

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add to PATH and PYTHONPATH
PATH=$PATH:$SCRIPT_DIR/combinato
PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/combinato
export PATH PYTHONPATH

# Loop over participants and perform clustering
for ppt_dir in */; do

    cd $ppt_dir

    # loop over .mat files and extract spikes
    for mat_file in *.mat; do
        css-extract --matfile $mat_file;
    done

    css-find-concurrent
    css-mask-artifacts
    css-plot-extracted

    for directory in ppt*/; do
        cd $directory
        h5_file=(*h5)

        # Prepare .txt for sorting
        css-prepare-sorting --neg --data $h5_file
        job_file=(*txt)

        # Cluster spikes
        css-cluster --jobs $job_file
        css-combine --jobs $job_file

        # Create summary plots 
        css-plot-sorted --neg --datafile $h5_file --label sort_neg_ada

        cd ..
    done

    cd ..
done