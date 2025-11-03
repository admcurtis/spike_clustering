#%% DEPENDENCIES
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import count_spikes
from glob import glob
import os
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE" # prevent errors loading H5 in WSL
import h5py

#%% I/O PATHS
data_path = "./processed_data/"
sensor_paths = glob(f"{data_path}*/*/", recursive = True)
sensor_paths = [os.path.normpath(path) for path in sensor_paths]

#%% FUNCTION
def sort_cluster_times(cluster_indx, times) -> dict[str, int]:
    temp_dict = defaultdict()
    for cluster in range(1, len(np.unique(cluster_indx))):
        temp_dict[f"{cluster}"] = times[cluster_indx == cluster]
    return temp_dict

#%% MAIN SCRIPT
all_dfs = []
for sensor_path in sensor_paths:

    ppt_num = sensor_path.split(os.sep)[-2][3:]
    sensor = sensor_path.split(os.sep)[-1][13:]

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
        f"./screeningData/20191202-041757-{ppt_num}-screeningData.mat",
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
        spikes_per_cluster[cluster] = count_spikes.count_spikes(spikes, stim_intervals)

    # --- create dataframe of the counted spikes ---
    rows = [
        {"unit": unit, "stimulus": stim, "spike_times": spikes}
        for unit, stim_dict in spikes_per_cluster.items()
        for stim, spikes in stim_dict.items()
    ]

    df = pd.DataFrame(rows)
    df.insert(0, "sensor", sensor)
    df.insert(0, "ppt", ppt_num)

    # all_intervals = np.array([
    #     interval 
    #     for stim_interval in stim_intervals.values()
    #     for interval in stim_interval
    # ])
    # baseline_intervals = [[i[0] - 0.7, i[0]] for i in all_intervals]

    # df["stim_times"] = [
    #     stim_intervals[stim] if stim != "BASELINE" else baseline_intervals
    #     for stim in df["stimulus"] 
    #     ]
    
    df["total_spikes"] = df["spike_times"].apply(lambda x: [len(i) for i in x])

    def conditional_extend(row):
        n = 300 if row["stimulus"] == "BASELINE" else 6
        l = row["total_spikes"].copy()
        l.extend([0] * n)
        l = l[:n]
        return l

    df["total_spikes"] = df.apply(conditional_extend, axis=1)

    df["mean_spikes"] = df["total_spikes"].apply(np.mean)
    df["median_spikes"] = df["total_spikes"].apply(np.median)
    df["std_spikes"] = df["total_spikes"].apply(np.std)

    all_dfs.append(df)

final_df = pd.concat(all_dfs, ignore_index=True)
final_df.to_csv("./spike_counts.csv", index=False)

