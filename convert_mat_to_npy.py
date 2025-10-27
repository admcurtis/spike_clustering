#%% DEPENDENCIES
from scipy.io import loadmat, savemat
import neo
import numpy as np


#%%
# Load the .mat file
data = loadmat(
    "./screeningData/20191202-041757-001-screeningData.mat",
    struct_as_record=False,
    squeeze_me=True
)

#%% INSPECT KEYS
print(data.keys())

#%% EXTRACT OUT AND IN
out = data["out"]
inn = data["in"]

#%% STIMULUS TIMINGS
pres_time = out.presTime
stim = out.stimulus

#%%
np.savez("ppt1_stim_timings.npz", pres_time=pres_time, stim=stim)


