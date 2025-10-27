#!bin/bash/

# set paths required by combinato
PATH=$PATH:/home/adam/workspace/ucl/spike_clustering/combinato
PYTHONPATH=$PYTHONPATH:/home/adam/workspace/ucl/spike_clustering/combinato
export PATH PYTHONPATH

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



