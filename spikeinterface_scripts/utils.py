import spikeinterface.full as si
import numpy as np
from tqdm import tqdm

def get_median_and_lsb(recording, num_random_chunks=10,
                       **random_chunk_kwargs):
    """This function estimates the channel-wise medians and the overal LSB from a recording

    Parameters
    ----------
    recording : si.BaseRecording
        The input recording object
    num_random_chunks : int, optional
        Number of random chunks to extract, by default 10
    **random_chunk_kwargs: keyword arguments for si.get_random_data_chunks() (mainly chunk_size)

    Returns
    -------
    int
        lsb_value
    np.array
        median_values
    """
    # compute lsb and median
    # gather chunks
    chunks = None
    for i in tqdm(range(num_random_chunks), desc="Extracting chunks"):
        chunks_i2 = si.get_random_data_chunks(
            recording, seed=i**2, **random_chunk_kwargs)
        if chunks is None:
            chunks = chunks_i2
        else:
            chunks = np.vstack((chunks, chunks_i2))

    lsb_value = 0
    num_channels = recording.get_num_channels()
    gain = recording.get_channel_gains()[0]
    dtype = recording.get_dtype()

    channel_idxs = np.arange(num_channels)
    min_values = np.zeros(num_channels, dtype=dtype)
    median_values = np.zeros(num_channels, dtype=dtype)
    offsets = np.zeros(num_channels, dtype=dtype)

    for ch in tqdm(channel_idxs, desc="Estimating channel stats"):
        unique_vals = np.unique(chunks[:, ch])
        unique_vals_abs = np.abs(unique_vals)
        lsb_val = np.min(np.diff(unique_vals))

        min_values[ch] = np.min(unique_vals_abs)
        median_values[ch] = np.median(chunks[:, ch]).astype(dtype)

        unique_vals_m = np.unique(chunks[:, ch] - median_values[ch])
        unique_vals_abs_m = np.abs(unique_vals_m)
        offsets[ch] = np.min(unique_vals_abs_m)

        if lsb_val > lsb_value:
            lsb_value = lsb_val

    return lsb_value, median_values
