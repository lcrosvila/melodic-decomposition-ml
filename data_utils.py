import numpy as np
import pandas as pd
import scipy.interpolate
from scipy.fftpack import dct, idct


def get_song_contours(
    processed_file,
    measure_resolution=-1,
    num_samples=100,
    random_seed=None,
    adaptable_resolution=False,
):
    # load the dataframe
    processed_file = pd.read_pickle(processed_file)
    contours = []
    durations = []
    ids = []

    for index, row in processed_file.iterrows():
        times = row["timespace"]
        pitches = row["pitchspace"]

        if adaptable_resolution:
            num_samples = int(times[-1] / min(times[1:] - times[:-1]))

        if measure_resolution < 0:
            # Interpolate the contour to get a fixed number of samples
            func = scipy.interpolate.interp1d(
                times / times[-1], pitches, kind="previous"
            )
            pitches_out = func(np.linspace(0, 1, num_samples))

            ids.append(row["title"])
            contours.append(pitches_out.astype(int))
            durations.append([times[-1]])
        else:
            measures = times / 6
            # get the indices where measures are multiples of measure_resolution
            indices = np.where(np.mod(measures, measure_resolution) == 0)[0]

            # if there is random_seed, shift every index by a random amount
            if random_seed is not None:
                np.random.seed(random_seed)
                indices = indices + np.random.randint(
                    0, measure_resolution, len(indices)
                )
                # remove the last index if it is out of bounds
                indices = indices[indices < len(times) - 1]

            for i in range(len(indices) - 1):
                start = indices[i]
                end = indices[i + 1]
                # Interpolate the contour of that section
                func = scipy.interpolate.interp1d(
                    (times[start:end] - times[start]) / (times[end - 1] - times[start]),
                    pitches[start:end],
                    kind="previous",
                )
                pitches_out = func(np.linspace(0, 1, num_samples))
                ids.append(row["title"] + "_" + str(i))
                contours.append(pitches_out.astype(int))
                durations.append([times[end] - times[start]])

    if adaptable_resolution:
        # fill contours with zeroes to make them the same length
        num_samples = max([len(c) for c in contours])
        for i in range(len(contours)):
            contours[i] = np.pad(contours[i], (0, num_samples - len(contours[i])))

    df = pd.DataFrame(np.concatenate([durations, contours], axis=1))
    df.columns = ["duration"] + list(range(num_samples))
    df.index = ids
    return df

def cosine_representation(contour, k=20, num_samples=100, order=1):
    """Converts a contour to a cosine representation. First, we get a fixed number of samples 
    from the contour by interpolating it. Then, we compute the DCT of the interpolated contour. 
    Finally, we truncate the DCT to get the cosine representation.

    Parameters
    ----------
    contour : dict
        A dictionary with two keys: 'pitches' (a list of all pitch values) and 
        'times' (a list of all offset values for the notes in the stream, including the final note).
    k : int
        The number of cosine coefficients to use in the cosine representation. The default is 20.
    num_samples : int, optional
        The number of samples to use in the cosine representation. The default is 100.
    order : int, optional
        The order of the DCT to compute. Can be 1 or 2. The default is 1 (i.e., compute only the first-order DCT).

    Returns
    -------
    numpy.ndarray
        The cosine representation.
    """

    times, pitches = contour['times'], contour['pitches']

    # interpolate the contour to get a fixed number of samples
    func = scipy.interpolate.interp1d(times/times[-1], pitches, kind='previous')

    if order == 1:
        cs = dct(func(np.linspace(0, 1, num_samples)), norm='ortho')
        # cs[k:] = 0 # truncate the cosine representation
        # get the k coefficients with maximum value and set the rest to zero
        cs[np.argsort(np.abs(cs))[:-k]] = 0
    elif order == 2:
        cs = dct(dct(func(np.linspace(0, 1, num_samples)), norm='ortho'), norm='ortho')
        # cs[k:] = 0 # truncate the cosine representation
        # get the k coefficients with maximum value and set the rest to zero
        cs[np.argsort(np.abs(cs))[:-k]] = 0
    else:
        raise ValueError("Order must be 1 or 2.")

    return cs

def reconstruct_signal_cosine(cs1, cs2=None):
    """Reconstructs a signal from one or two cosine representations.

    Parameters
    ----------
    cs1 : numpy.ndarray
        The first-order cosine representation.
    cs2 : numpy.ndarray, optional
        The second-order cosine representation. If None (default), only the first-order representation is used.
    k : int, optional
        If cs2 is provided, the number of cosine coefficients is needed for The reconstruction. The default is 20.
    num_samples : int, optional
        The number of samples to use in the reconstruction. The default is 100.

    Returns
    -------
    numpy.ndarray
        The reconstructed signal.
    """

    if cs2 is not None:
        # Apply the inverse second-order DCT to get the intermediate signal
        int_signal = idct(idct(cs2, norm='ortho'), norm='ortho')

        # Apply the inverse first-order DCT to get the final reconstructed signal and sum with the intermediate signal
        return (idct(cs1, norm='ortho') + int_signal) / 2
    else:
        # Only first-order DCT is used
        return idct(cs1, norm='ortho')