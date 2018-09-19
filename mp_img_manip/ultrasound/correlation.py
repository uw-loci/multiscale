"""Script for performing correlations/PSF calculations on ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import numpy as np
from pathlib import Path
import scipy.signal as sig

import mp_img_manip.utility_functions as util
import mp_img_manip.ultrasound.reconstruction as recon


def define_correlation_window(params_acquisition: dict):
    """Define the window over which the correlation is calculated inside the frame"""

    params_window = dict({'Elevational size mm':1,
                          'Lateral size mm': 1,
                          'Axial size mm': 1,
                          'Start of depth range mm': 6,
                          'End of depth range mm': 8,
                          'Depth step mm': 0.25})

    params_window['axial resolution'] = 1540E3 / 62.5E6
    #params_window['axial resolution'] = params_acquisition['sampling frequency']/params_acquisition['speed of sound']
    params_window['lateral resolution'] = 0.1
    params_window['elevational resolution'] = 0.2 # todo: func to read in position vec and grab this

    return params_window


def determine_window_sweep():
    """Define the range the window sweeps over within the frames"""
    return


def detrend_along_dimension(array_im: np.ndarray, dim_detrend: int) -> np.ndarray:
    """Detrend along a dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """

    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    return array_detrend


def detrend_along_dimension_and_subtract_mean(array_im: np.ndarray, dim_detrend: int, dim_to_average: int) -> np.ndarray:
    """Detrend along a dimension, and subtract a mean of the detrend along another dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """

    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    array_mean = np.mean(array_detrend, dim_to_average)
    shape_array = np.shape(array_detrend)

    if dim_to_average is 2: # lateral
        array_detrend_avg = array_detrend - array_mean[:, :, None]
    elif dim_to_average is 1: # axial
        array_detrend_avg = array_detrend - np.reshape(array_mean, [shape_array[0], 1, shape_array[2]])
    elif dim_to_average is 0: # elevation
        array_detrend_avg = array_detrend - array_mean
    else:
        raise ValueError('Please enter a valid dimension (0, 1, or 2)')

    return array_detrend_avg


def calculate_1d_autocorrelation(line: np.ndarray, shift: int) -> np.double:
    """Calculate the correlation matrix for a certain shift, returning the correlation between the shifted lines"""
    n = len(line)
    coef_matrix = np.corrcoef(line[0:n-shift], line[shift:n])
    coef = coef_matrix[0, 1]

    return coef


def calculate_1d_autocorrelation_curve(window: np.ndarray, dim_of_corr: int, threshold: np.double=0.1) -> np.ndarray:
    """Calculate the auto-correlation curve along a submitted dimension.  Averages over all 1d lines in array
    """

    shape_window = np.shape(window)
    corr_curve = []

    for shift in range(int(shape_window[dim_of_corr]/2 + 1)):
        corr_along_lines = np.apply_along_axis(calculate_1d_autocorrelation, dim_of_corr, window, shift)
        average_corr = np.mean(corr_along_lines)
        if average_corr < threshold:
            break

        corr_curve.append(average_corr)

    return corr_curve


def calculate_1d_autocorrelation_curve_ind_avg(window: np.ndarray, dim_of_corr: int, dim_of_avg: int) -> np.ndarray:
    """Calculate the auto-correlation curve along a submitted dimension. Averages over one axis, then remaininf axis"""

    shape_window = np.shape(window)
    corr_curve = []

    for shift in range(int(shape_window[dim_of_corr]/2 + 1)):
        corr_along_lines = np.apply_along_axis(calculate_1d_autocorrelation, dim_of_corr, window, shift)
        first_avg = np.mean(corr_along_lines, dim_of_avg)
        average_corr = np.mean(first_avg)
        corr_curve.append(average_corr)

    return corr_curve


def calculate_curves_per_window(window: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """Calculate the elevation, axial, and lateral autocorrelation curves using whole window averaging

    Input:
    Window: a 3d numpy array over which to calculate the correlation

    Output:
    curve_elevation: 1d correlation curve along elevational axis y
    curve_axial: 1d correlation curve along axial axis z
    curve_lateral: 1d correlation curve along lateral axis x
    """
    curve_elevation = calculate_1d_autocorrelation_curve(window, 0)
    curve_axial = calculate_1d_autocorrelation_curve(window, 1)
    curve_lateral = calculate_1d_autocorrelation_curve(window, 2)

    return curve_elevation, curve_axial, curve_lateral


def calculate_curves_per_window_ind_avg(window: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """Calculate the elevation, axial, and lateral autocorrelation curves using frame, or lateral, averaging first

    Input:
    Window: a 3d numpy array over which to calculate the correlation

    Output:
    curve_elevation: 1d correlation curve along elevational axis y
    curve_axial: 1d correlation curve along axial axis z
    curve_lateral: 1d correlation curve along lateral axis x
    """
    curve_elevation = calculate_1d_autocorrelation_curve_ind_avg(window, 0, 2)
    curve_axial = calculate_1d_autocorrelation_curve_ind_avg(window, 1, 0)
    curve_lateral = calculate_1d_autocorrelation_curve_ind_avg(window, 2, 0)

    return curve_elevation, curve_axial, curve_lateral


def calculate_correlation_curves_at_all_depths(window_shape: np.ndarray, depths_start_end: np.ndarray):
    """For each starting window depth, calculate each correlation curve"""
    return


def load_iq(dir_iq: Path) -> (np.ndarray, dict):
    list_iq = recon.get_sorted_list_mats(dir_iq, search_str='mat')
    array_iq, params = recon.mat_list_to_iq_array(list_iq)

    return array_iq, params


def iq_to_envelope(iq_array: np.ndarray) -> np.ndarray:
    """"Detrend iq along axial direction then use hilbert transform to get envelope"""

    env = np.abs(iq_array)
    env_detrended = detrend_along_dimension(env, 1)

    return env_detrended


def detrend_and_square_window(window: np.ndarray) -> np.ndarray:
    """Detrend the window, adding the pre-detrend mean to prevent frequency loss, then squaring to get intensity"""
    shape_array = np.shape(window)
    axial_means = np.mean(window, 1)

    window_detrended = detrend_along_dimension(window, 1)
    window_mean_added = window_detrended + np.reshape(axial_means, [shape_array[0], 1, shape_array[2]])
    window_squared = np.square(window_mean_added)

    return window_squared


def calc_corr_curves(env_array: np.ndarray, window_params: dict) -> np.ndarray:
    idx_start = int(np.floor(window_params['Start of depth range mm']/window_params['axial resolution']))
    idx_end = int(np.floor(window_params['End of depth range mm']/window_params['axial resolution']))

    window = env_array[:, idx_start:idx_end]
    window_squared = detrend_and_square_window(window)

    curves = calculate_curves_per_window(window_squared)
    curves_ind_avg = calculate_curves_per_window_ind_avg(window_squared)

    return curves, curves_ind_avg


def plot_corr_curve(curve_1d: np.ndarray, spacing: np.double, threshold: np.double=0.1):
    return


def plot_curves(array_curves: np.ndarray, params_acq: dict, dir_output: Path, suffix_output: 'str'):
    return


def calc_plot_corr_curves(dir_iq: Path, dir_output: Path=None, suffix_output: str=None):
    iq_array, params_acquisition = load_iq(dir_iq)
    env_array = iq_to_envelope(iq_array)

    params_window = define_correlation_window(params_acquisition)
    curves, curves_ind_avg = calc_corr_curves(env_array, params_window)

    plot_curves(curves, params_window, dir_output, suffix_output)
    plot_curves(curves_ind_avg, params_window, dir_output, suffix_output + '_IndAvg')
