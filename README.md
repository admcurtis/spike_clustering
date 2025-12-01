# Spike clustering using Combinato

The scripts found here convert `.ns6` files—containing time series for each channel per participant—into separate `.mat` files.  
Each `.mat` file contains the data for a single channel.

`.ns6` files can be converted to `.mat` using `convert_ns6_to_mat.py`.

Once converted, spike sorting can be performed from the command line using `cluster_data.sh`.

The clustering requires a [Combinato installation](https://github.com/jniediek/combinato/).

Once clustered, the data can be aligned with behavioural data using `count_spikes_per_stimulus.py`.  
This will save a `.csv` with spike counts, and the mean, median, and standard deviation for each stimulus and baseline period.

From there, the presence of concept cells can be determined using `detect_concepts.py`.  
This script follows the analysis procedure presented in [Quiroga et al. (2005)](https://pubmed.ncbi.nlm.nih.gov/15973409/).
