#%% DEPENDENCIES
import numpy as np
import pandas as pd

#%% FIND CONCEPT CELLS
spike_data = pd.read_csv("./spike_counts.csv")

baselines = spike_data[spike_data["stimulus"] == "BASELINE"].copy()
stims = spike_data[spike_data["stimulus"] != "BASELINE"].copy()

baselines["sigma"] = baselines["mean_spikes"].copy() + (baselines["std_spikes"] * 1.96)

sigmas = baselines[["ppt", "sensor", "unit", "sigma"]]
stims = pd.merge(stims, sigmas)

stims["concept_cell"] = np.where(
    stims["median_spikes"] > stims["sigma"],
    1,
    0
)

concepts = stims[stims["concept_cell"] == 1]

print(concepts)
