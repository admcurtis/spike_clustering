#%% DEPENDENCIES
# type: ignore
from scipy.io import savemat
import neo # for .ns6
import numpy as np
import os

#%% Load data and convert to .mat

os.makedirs("processed_data", exist_ok=True)

files = os.listdir("ieeg_data")

for file in files: 

    # File and participant
    filename = f"ieeg_data/{file}"
    ppt = file[16:19]

    # Load .ns6
    reader = neo.io.BlackrockIO(filename=filename)
    block = reader.read_block()

    # Extract signal
    signal = block.segments[0].analogsignals[0]  
    data = np.array(signal)

    # Extract sampling rate
    sr = float(signal.sampling_rate)

    # Create .mat structure
    mat_struct = {"data": data, "sr": sr}

    # Loop over sensors and create structure for each, save as .mat
    for sensor in range(0, mat_struct["data"].shape[1]):

        save_path = f"processed_data/ppt{ppt}/"
        os.makedirs(save_path, exist_ok=True)

        save_name = f"ppt{ppt}_sensor{sensor}.mat"

        temp_data = mat_struct.copy()
        this_sensor = temp_data["data"][:,sensor]
        temp_data["data"] = this_sensor

        # Save .mat
        savemat(save_path + save_name, temp_data)

