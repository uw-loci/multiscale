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


def detrend_axial_global(array_im: np.ndarray, axial_dim: int=1, lateral_dim: int=0) -> np.ndarray:
    """Detrend each column of the 3D image"""
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


