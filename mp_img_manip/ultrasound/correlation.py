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

    return array_detrend_mean


def detrend_axial_global(array_im: np.ndarray, axial_dim: int=1, lateral_dim: int=2) -> np.ndarray:
    """Detrend along the axial dimension, for each lateral frame

    Defaults assumes
    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral

    """
    array_detrend = sig.detrend(array_im, axis=axial_dim)
    mean_detrend = np.mean(array_detrend, lateral_dim)

    array_detrend = array_detrend - mean_detrend

    return array_detrend


def detrend_window():
    """Detrend the window"""
    return


def calculate_1d_correlation_curve():
    """Calculate the correlation curve along a submitted dimension"""
    return


