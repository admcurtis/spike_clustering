import numpy as np

def group_spikes(spike_times, stim_duration=0.7) -> list[list]:
    """
    Takes list of all spikes to a given stimulus across trials
    and returns list of lists with each sublist concerning a single trial
    """
    if len(spike_times) == 0:
        return []
    diffs = np.diff(spike_times)
    split_indices = np.where(diffs > stim_duration)[0] + 1
    split_stims = np.split(spike_times, split_indices)
    return [stim.tolist() for stim in split_stims]



def count_spikes(spike_times, stim_intervals) -> dict[str, list]:
    """
    For a cluster (neuron), count the number of times the unit spiked for each stimulus 
    and during the baseline periods

    Returns a dict with stimuli as keys and a list of spikes as values
    The final key is BASELINE indicating when the neuron fired during
    the baseline period.
    """

    # Get spikes to a stimulus acorss all trials
    stim_spikes = {
        stim: spike_times[np.any(
            (spike_times[:, None] >= (intervals[:, 0] + 0.3)) & # +0.3 = 300 ms after stim onset
            (spike_times[:, None] <= intervals[:, 1]),
            axis=1
        )]
        for stim, intervals in stim_intervals.items()
    }

    # group spikes by trial
    stim_spikes = {k: group_spikes(v) for k,v in stim_spikes.items()}

    all_intervals = np.array([
        interval 
        for stim_interval in stim_intervals.values()
        for interval in stim_interval
    ])

    # Baseline: -700ms - 0ms 
    # all spikes that are less that stim onset but greater than onset - 0.7
    baseline_spikes = spike_times[np.any(
            (spike_times[:, None] <= all_intervals[:, 0]) &
            (spike_times[:, None] >= all_intervals[:, 0] - 0.7),
            axis=1
        )]
    
    # group baseline spikes per trial
    baseline_spikes = group_spikes(baseline_spikes)
    
    stim_spikes["BASELINE"] = baseline_spikes
    
    return stim_spikes