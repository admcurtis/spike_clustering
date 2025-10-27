#%% DEPENDENCIES
# type: ignore
from scipy.io import loadmat
import h5py
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd

#%% I/O PATHS
ppt_num = "003"
sensor = 0

data_path = "/home/adam/workspace/ucl/processed_data/"
ppt_sensor_path = f"{data_path}/ppt{ppt_num}/ppt{ppt_num}_sensor{sensor}"

#%% LOAD CLUSTERED SPIKES
ppt_data = h5py.File(f"{ppt_sensor_path}/data_ppt003_sensor0.h5", "r") 
list(ppt_data.items())

#%% SORTING DATA
neg_sort_file = f"{ppt_sensor_path}/sort_neg_simple/sort_cat.h5"
neg_sort_data = h5py.File(neg_sort_file, "r")

pos_sort_file = f"{ppt_sensor_path}/sort_pos_simple/sort_cat.h5"
pos_sort_data = h5py.File(pos_sort_file, "r")

neg_cluster_indx = np.array(neg_sort_data["classes"])
pos_cluster_indx = np.array(pos_sort_data["classes"])

#%% EXTRACT THE SPIKES AND THEIR TIMES
# spikes with negative deflections
neg_spikes = ppt_data["neg"]["spikes"][:]
neg_times = ppt_data["neg"]["times"][:] / 1000 # convert ms to seconds

# spikes with positive deflections
pos_spikes = ppt_data["pos"]["spikes"][:]
pos_times = ppt_data["pos"]["times"][:] / 1000 # convert ms to seconds

#%% SORT CLUSTERS INTO DICTIONARIES
def sort_cluster_times(cluster_indx, times) -> dict[str, int]:
    temp_dict = defaultdict()
    for cluster in range(1, len(np.unique(cluster_indx))):
        temp_dict[f"{cluster}"] = times[cluster_indx == cluster]
    return temp_dict

neg_clusters = sort_cluster_times(neg_cluster_indx, neg_times)
pos_clusters = sort_cluster_times(pos_cluster_indx, pos_times)

#%% PLOT INDIVIDUAL SPIKES
waveform = neg_spikes[5]  
plt.plot(waveform)
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.show()

#%% LOAD BEHAVIOURAL DATA
# Load the .mat file
behave_data = loadmat(
    "./screeningData/20191202-041757-003-screeningData.mat",
    struct_as_record=False,
    squeeze_me=True
)
print(behave_data.keys())

behave_output = behave_data["out"] # this is the data and timing
print(behave_output._fieldnames)

#%% STIMULUS TIMINGS
pres_time = behave_output.presTime # shape: 50, 6, 2; stimulus x presentation x start-end
stim = behave_output.stimulus # shape: 50; stimulus names

#%% DICTIONAIRES FOR COUNTING SPIKES
stim_intervals = dict(zip(stim, pres_time))

#%% VECTORISE SPIKE COUNTING (FASTER)
# produces the same dictionary as the block above but in a faster vectorised way.
# Better for larger datasets but less readable.
def count_spikes(spike_times, stim_intervals) -> dict[str, list]:
    """
    For a cluster, count the number of times the unit spiked for each stimulus
    """
    stim_counts = {
        stim: spike_times[np.any(
            (spike_times[:, None] >= intervals[:, 0]) &
            (spike_times[:, None] <= intervals[:, 1]),
            axis=1
        )]
        for stim, intervals in stim_intervals.items()
    }
    return stim_counts

#%%
spikes_per_cluster = {key: None for key, _ in neg_clusters.items()}

for cluster, spikes in neg_clusters.items():
    spikes_per_cluster[cluster] = count_spikes(spikes, stim_intervals)

#%% CONVERT TO DF
rows = [
    {"unit": unit, "stimulus": stim, "spike_times": spikes}
    for unit, stim_dict in spikes_per_cluster.items()
    for stim, spikes in stim_dict.items()
]

# create DataFrame
df = pd.DataFrame(rows)

df["total_spikes"] = df["spike_times"].apply(len)
