import numpy as np

# code copied from https://github.com/int-brain-lab/ibllib/blob/f05d8bb84eb2464a5bd88c7186733379359ff252/brainbox/task/trials.py

def bincount2D(x, y, xbin=0, ybin=0, xlim=None, ylim=None, weights=None):
    """
    Computes a 2D histogram by aggregating values in a 2D array.
    :param x: values to bin along the 2nd dimension (c-contiguous)
    :param y: values to bin along the 1st dimension
    :param xbin:
        scalar: bin size along 2nd dimension
        0: aggregate according to unique values
        array: aggregate according to exact values (count reduce operation)
    :param ybin:
        scalar: bin size along 1st dimension
        0: aggregate according to unique values
        array: aggregate according to exact values (count reduce operation)
    :param xlim: (optional) 2 values (array or list) that restrict range along 2nd dimension
    :param ylim: (optional) 2 values (array or list) that restrict range along 1st dimension
    :param weights: (optional) defaults to None, weights to apply to each value for aggregation
    :return: 3 numpy arrays MAP [ny,nx] image, xscale [nx], yscale [ny]
    """
    # if no bounds provided, use min/max of vectors
    if xlim is None:
        xlim = [np.min(x), np.max(x)]
    if ylim is None:
        ylim = [np.min(y), np.max(y)]

    def _get_scale_and_indices(v, bin, lim):
        # if bin is a nonzero scalar, this is a bin size: create scale and indices
        if np.isscalar(bin) and bin != 0:
            scale = np.arange(lim[0], lim[1] + bin / 2, bin)
            ind = (np.floor((v - lim[0]) / bin)).astype(np.int64)
        # if bin == 0, aggregate over unique values
        else:
            scale, ind = np.unique(v, return_inverse=True)
        return scale, ind

    xscale, xind = _get_scale_and_indices(x, xbin, xlim)
    yscale, yind = _get_scale_and_indices(y, ybin, ylim)
    # aggregate by using bincount on absolute indices for a 2d array
    nx, ny = [xscale.size, yscale.size]
    ind2d = np.ravel_multi_index(np.c_[yind, xind].transpose(), dims=(ny, nx))
    r = np.bincount(ind2d, minlength=nx * ny, weights=weights).reshape(ny, nx)

    # if a set of specific values is requested output an array matching the scale dimensions
    if not np.isscalar(xbin) and xbin.size > 1:
        _, iout, ir = np.intersect1d(xbin, xscale, return_indices=True)
        _r = r.copy()
        r = np.zeros((ny, xbin.size))
        r[:, iout] = _r[:, ir]
        xscale = xbin

    if not np.isscalar(ybin) and ybin.size > 1:
        _, iout, ir = np.intersect1d(ybin, yscale, return_indices=True)
        _r = r.copy()
        r = np.zeros((ybin.size, r.shape[1]))
        r[iout, :] = _r[ir, :]
        yscale = ybin

    return r, xscale, yscale

def get_event_aligned_raster(times, 
        events, tbin=0.02, values=None, epoch=[-0.4, 1], bin=True):
    """
    Get event aligned raster
    :param times: array of times e.g spike times or dlc points
    :param events: array of events to epoch around
    :param tbin: bin size to over which to count events
    :param values: values to scale counts by
    :param epoch: window around each event
    :param bin: whether to bin times in tbin windows or not
    :return:
    """

    if bin:
        vals, bin_times, _ = bincount2D(times, np.ones_like(times), xbin=tbin, weights=values)
        vals = vals[0]
        t = np.arange(epoch[0], epoch[1] + tbin, tbin)
        nbin = t.shape[0]
    else:
        vals = values
        bin_times = times
        tbin = np.mean(np.diff(bin_times))
        t = np.arange(epoch[0], epoch[1], tbin)
        nbin = t.shape[0]

    # remove nan trials
    non_nan_events = events[~np.isnan(events)]
    nan_idx = np.where(~np.isnan(events))
    intervals = np.c_[non_nan_events + epoch[0], non_nan_events + epoch[1]]

    # Remove any trials that are later than the last value in bin_times
    out_intervals = intervals[:, 1] > bin_times[-1]
    epoch_idx = np.searchsorted(bin_times, intervals)[np.invert(out_intervals)]

    #print(nbin)
    ##print(vals)
    #print(epoch_idx)

    for ep in range(nbin):
        if ep == 0:
            event_raster = (vals[epoch_idx[:, 0] + ep]).astype(float)
        else:
            event_raster = np.c_[event_raster, vals[epoch_idx[:, 0] + ep]]

    # Find any trials that are less than the first value time and fill with nans (case for example
    # where spiking of cluster doesn't start till after start of first trial due to settling of
    # brain)
    event_raster[intervals[np.invert(out_intervals), 0] < bin_times[0]] = np.nan

    # Add back in the trials that were later than last value with nans
    if np.sum(out_intervals) > 0:
        event_raster = np.r_[event_raster, np.full((np.sum(out_intervals),
                                                    event_raster.shape[1]), np.nan)]
        assert event_raster.shape[0] == intervals.shape[0]

    # Reindex if we have removed any nan values
    all_event_raster = np.full((events.shape[0], event_raster.shape[1]), np.nan)
    all_event_raster[nan_idx, :] = event_raster

    return all_event_raster, t
