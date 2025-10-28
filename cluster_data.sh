#!bin/bash/

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

    for directory in */; do
        cd $directory
        h5_file=(*h5)
        
        # cluster negative and positive spikes
        css-simple-clustering --neg --datafile $h5_file
        css-simple-clustering --datafile $h5_file

        # create summary plots for negative and positive spikes
        css-plot-sorted --neg --datafile $h5_file --label sort_neg_simple
        css-plot-sorted --datafile $h5_file --label sort_pos_simple

        cd ..
    done

    cd ..
done


