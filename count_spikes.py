import numpy as np

def count_spikes(spike_times, stim_intervals) -> dict[str, list]:
    """
    For a cluster (neuron), count the number of times the unit spiked for each stimulus 
    and during the baseline periods

    Returns a dict with stimuli as keys and a list of spikes as values
    The final key is BASELINE indicating when the neuron fired during
    the baseline period.
    """
    stim_spikes = {
        stim: spike_times[np.any(
            (spike_times[:, None] >= intervals[:, 0]) &
            (spike_times[:, None] <= intervals[:, 1]),
            axis=1
        )]
        for stim, intervals in stim_intervals.items()
    }

    all_intervals = np.array([
        interval 
        for stim_interval in stim_intervals.values()
        for interval in stim_interval
    ])

    baseline_spikes = spike_times[~np.any(
            (spike_times[:, None] >= all_intervals[:, 0]) &
            (spike_times[:, None] <= all_intervals[:, 1]),
            axis=1
        )]
    
    stim_spikes["BASELINE"] = baseline_spikes
    
    return stim_spikes