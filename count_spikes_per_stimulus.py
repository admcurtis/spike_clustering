#%% DEPENDENCIES
from scipy.io import loadmat
import h5py
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from count_spikes import count_spikes
from glob import glob

#%% I/O PATHS
data_path = "/home/adam/workspace/ucl/spike_clustering/processed_data/"
sensor_paths = glob(f"{data_path}*/*/", recursive = True)

#%% FUNCTION
def sort_cluster_times(cluster_indx, times) -> dict[str, int]:
    temp_dict = defaultdict()
    for cluster in range(1, len(np.unique(cluster_indx))):
        temp_dict[f"{cluster}"] = times[cluster_indx == cluster]
    return temp_dict

#%% MAIN SCRIPT
all_dfs = []
for sensor_path in sensor_paths:

    ppt_num = sensor_path.split("/")[-3][3:]
    sensor = sensor_path.split("/")[-2][13:]

    # --- load h5 data containing spikes ---
    ppt_data = h5py.File(f"{sensor_path}/data_ppt{ppt_num}_sensor{sensor}.h5", "r") 

    # --- spikes with negative deflections ---
    neg_spikes = ppt_data["neg"]["spikes"][:]
    neg_times = ppt_data["neg"]["times"][:] / 1000 # convert ms to seconds

    # --- spikes with positive deflections ---
    pos_spikes = ppt_data["pos"]["spikes"][:]
    pos_times = ppt_data["pos"]["times"][:] / 1000 # convert ms to seconds

    # --- load sorting file containing cluster info ---
    try:
        neg_sort_file = f"{sensor_path}/sort_neg_simple/sort_cat.h5"
        neg_sort_data = h5py.File(neg_sort_file, "r")
        pos_sort_file = f"{sensor_path}/sort_pos_simple/sort_cat.h5"
        pos_sort_data = h5py.File(pos_sort_file, "r")
    except FileNotFoundError:
        print(f"No units detected for ppt{ppt_num} sensor{sensor}")
        continue

    # --- indices for which spikes are in which clusters ---
    neg_cluster_indx = np.array(neg_sort_data["classes"])
    pos_cluster_indx = np.array(pos_sort_data["classes"])

    # --- sort the spikes into thier clusters ---
    neg_clusters = sort_cluster_times(neg_cluster_indx, neg_times)
    pos_clusters = sort_cluster_times(pos_cluster_indx, pos_times)

    # --- continue if all spikes were unassigned ---
    if not neg_clusters:
        continue
    
    behave_data = loadmat(
        f"./screeningData/{ppt_num}-screeningData.mat",
        struct_as_record=False,
        squeeze_me=True
    )

    behave_output = behave_data["out"] # this is the data and timing

    pres_time = behave_output.presTime # shape: 50, 6, 2; stimulus x presentation x start-end
    stim = behave_output.stimulus # shape: 50; stimulus names

    # --- count the spikes the occured for each stimulus and the baseline ---
    stim_intervals = dict(zip(stim, pres_time))
    spikes_per_cluster = {key: None for key, _ in neg_clusters.items()}

    for cluster, spikes in neg_clusters.items():
        spikes_per_cluster[cluster] = count_spikes(spikes, stim_intervals)

    # --- create dataframe of the counted spikes ---
    rows = [
        {"unit": unit, "stimulus": stim, "spike_times": spikes}
        for unit, stim_dict in spikes_per_cluster.items()
        for stim, spikes in stim_dict.items()
    ]

    df = pd.DataFrame(rows)
    df.insert(0, "sensor", sensor)
    df.insert(0, "ppt", ppt_num)
    df["total_spikes"] = df["spike_times"].apply(len)

    all_dfs.append(df)

final_df = pd.concat(all_dfs, ignore_index=True)
final_df.to_csv("./spike_counts.csv", index=False)


