import pandas as pd
import numpy as np

def align_spikes(times, events, epoch, bin_size=None):

    """
    Align spikes to a set of event times.

    If the optional `bin_size` argument is supplied, the spike 
    times are binned.

    Implemented purely in Pandas

    Limitation: can't have overlapping trials

    Parameters
    ----------
    times : numpy.ndarray
        The timestamps to align (in seconds)
    events : numpy.ndarray
        The reference times (in seconds)
    epoch : tuple
        Start and end of the window size around the events
    bin_size : float
        Bin size (in seconds); if None, then individual times will be returned

    Returns
    -------
    If bin_size is None:
        DataFrame with aligned times
    Otherwise:
        numpy.ndarray of spike counts per bin

    """

    ii = pd.IntervalIndex.from_arrays(
        events + epoch[0], 
        events + epoch[1])

    a = pd.cut(pd.Series(data = times), ii)

    df = pd.DataFrame(index = times, 
        data = {'interval' : a.values}).dropna()

    groups = df.groupby('interval').ngroup()

    df['spike_times'] = events[groups.values]
    df['trial_index'] = groups.values

    df.set_index(df.index.values - df['spike_times'], inplace=True)

    df = df.drop(columns=["interval", "spike_times"])

    if bin_size is None:
        
        return df
    
    else:

        bins = np.arange(epoch[0], epoch[1] + bin_size, bin_size)
        a = pd.cut(pd.Series(data = df.index.values), 
                   bins = bins)
        
        df2 = pd.DataFrame(data = {'interval' : a.values})

        groups = df2.groupby('interval').ngroup()

        df['bin_index'] = groups.values

        counts = np.zeros((events.size, bins.size))

        for i in range(len(events)):
            b, c = np.unique(df[df.trial_index == i].bin_index, return_counts=True)
            counts[i,b] = c

        return counts


def align_lfp(lfp, events, epoch):

    """
    Align lfp to a set of event times.

    Implemented purely in Pandas/xarray

    Parameters
    ----------
    lfp : xarray.DataArray
        times x channels
    events : numpy.ndarray
        The reference times (in seconds)
    epoch : tuple
        Start and end of the window size around the events

    Returns
    -------
    xarray.DataArray
        The aligned LFP (times x channels x trials)
    """

    sample_interval = np.mean(np.diff(lfp.time[:1000]))
    presentation_ids = np.arange(len(events))

    trial_window = np.arange(epoch[0], epoch[1], sample_interval)
    time_selection = np.concatenate([trial_window + t for t in events])

    inds = pd.MultiIndex.from_product((presentation_ids, trial_window), 
                                    names=('presentation_id', 'time_from_presentation_onset'))

    ds = lfp.sel(time = time_selection, method='nearest').to_dataset(name = 'aligned_lfp')
    ds = ds.assign(time=inds).unstack('time')

    aligned_lfp = ds['aligned_lfp']

    return aligned_lfp