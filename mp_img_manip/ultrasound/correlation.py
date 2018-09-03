"""Script for performing correlations/PSF calculations on ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import numpy as np
import scipy.signal as sig


def define_correlation_window(dimens_window: np.ndarray):
    """Define the window over which the correlation is calculated inside the frame"""

    params_window = {}
    params_window['Dimensions'] = dimens_window
    params_window['Elevational size'] = 5
    params_window['Lateral size'] = 5

    params_window['Depth'] = 5

    return


def determine_window_sweep():
    """Define the range the window sweeps over within the frames"""
    return


def detrend_along_dimension(array_im: np.ndarray, dim_detrend: int, dim_to_average: int) -> np.ndarray:
    """Detrend along a dimension, and subtract a mean of the detrend along another dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """

    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    array_mean = np.mean(array_detrend, dim_to_average)

    shape_array = np.shape(array_detrend)

    if dim_to_average is 2:
        array_detrend_mean = array_detrend - array_mean[:, :, None]
    elif dim_to_average is 1:
        array_detrend_mean = array_detrend - np.reshape(array_mean, [shape_array[0], 1, shape_array[2]])
    elif dim_to_average is 0:
        array_detrend_mean = array_detrend - array_mean
    else:
        raise ValueError('Please enter a valid dimension (0, 1, or 2)')

    return array_detrend_mean


def calculate_1d_correlation_curve(
        window: np.ndarray, params_window: dict, dim_of_corr: int, dim_of_averaging: int) -> np.ndarray:

    """Calculate the correlation curve along a submitted dimension"""

    shape_window = np.shape(window)

    for shift in range(int(shape_window[dim_of_corr]/2 + 1)):
        for dim_loc in range(1, int(shape_window[dim_of_corr]/2)):
            for frame in range(shape_window[dim_of_averaging]):
                print('Do something')
    return np.array([4, 3])


def calculate_correlation_curves_at_all_depths():
    """For each starting window depth, calculate each correlation curve"""
    return



