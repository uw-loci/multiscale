"""Script for performing correlations/PSF calculations on ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import numpy as np

def define_correlation_window(dimens_window: np.ndarray) -> :
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


def detrend_global():
    """Detrend the entire 3D image"""
    return


def detrend_window():
    """Detrend the window"""
    return


def calculate_1d_correlation_curve():
    """Calculate the correlation curve along a submitted dimension"""
    return


