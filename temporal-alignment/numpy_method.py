import numpy as np

def align_spikes(times, events, epoch, bin_size=None):

    """
    Align spikes to a set of event times.

    If the optional `bin_size` argument is supplied, the spike 
    times are binned.

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
    DataFrame
        The aligned times, optionally with a `bin_index` column
    """
    
    if bin_size is not None:
        bins = np.arange(epoch[0], epoch[1] + bin_size, bin_size)
        counts = np.zeros((events.size, bins.size-1))

    ts = [ ]
    trials = [ ]
    
    for i, start in enumerate(events):
        startInd = np.searchsorted(times, start+epoch[0])
        endInd = np.searchsorted(times, start+epoch[1])

        if bin_size is not None:
            counts[i,:] = np.histogram(times[startInd:endInd] - start, bins)[0]
        else:
            ts.append(times[startInd:endInd] - start)
            trials.append(np.zeros((endInd-startInd,)) + i)

    if bin_size is not None:
        return bins, counts
    else:
        return np.concatenate(ts), np.concatenate(trials)


def align_lfp(times, lfp, events, epoch):

    """
    Align LFP to a set of event times.

    Parameters
    ----------
    times : numpy.ndarray
        The timestamps of the data to align
    lfp : numpy.ndarray
        The data to align (times x channels)
    events : numpy.ndarray
        The reference times (in seconds)
    epoch : tuple
        Start and end of the window size around the events

    Returns
    -------
    numpy.ndarray
        Times x channels x trials
    """
    
    trials = [ ]
    
    for i, start in enumerate(events):
        startInd = np.searchsorted(times, start + epoch[0])
        endInd = np.searchsorted(times, start + epoch[1])

        trials.append(lfp[startInd:endInd,:])

        if (i == 0):
            ts = times[startInd:endInd] - start

    return ts, np.stack(trials, axis=2)