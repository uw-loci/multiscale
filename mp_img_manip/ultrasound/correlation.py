"""Script for performing correlations/PSF calculations on ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import numpy as np
from pathlib import Path
import scipy.signal as sig

import mp_img_manip.utility_functions as util
import mp_img_manip.ultrasound.reconstruction as recon

def define_correlation_window(dimens_window: np.ndarray):
    """Define the window over which the correlation is calculated inside the frame"""

    params_window = dict
    params_window['Dimensions'] = dimens_window
    params_window['Elevational size'] = 5
    params_window['Lateral size'] = 5
    params_window['Axial size'] = 5
    params_window['Depth'] = 5

    return params_window


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
        array_detrend_avg = array_detrend - array_mean[:, :, None]
    elif dim_to_average is 1:
        array_detrend_avg = array_detrend - np.reshape(array_mean, [shape_array[0], 1, shape_array[2]])
    elif dim_to_average is 0:
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


def calculate_1d_autocorrelation_curve(window: np.ndarray, dim_of_corr: int) -> np.ndarray:
    """Calculate the auto-correlation curve along a submitted dimension
    """

    shape_window = np.shape(window)
    corr_curve = []

    for shift in range(int(shape_window[dim_of_corr]/2 + 1)):
        corr_along_lines = np.apply_along_axis(calculate_1d_autocorrelation, dim_of_corr, window, shift)
        average_corr = np.mean(corr_along_lines)
        corr_curve.append(average_corr)
    return corr_curve


def calculate_1d_autocorrelation_curve_ind_avg(window: np.ndarray, dim_of_corr: int, dim_of_avg: int) -> np.ndarray:
    """Calculate the auto-correlation curve along a submitted dimension"""

    shape_window = np.shape(window)
    corr_curve = []

    for shift in range(int(shape_window[dim_of_corr]/2 + 1)):
        corr_along_lines = np.apply_along_axis(calculate_1d_autocorrelation, dim_of_corr, window, shift)
        first_avg = np.mean(corr_along_lines, dim_of_avg)
        average_corr = np.mean(first_avg)
        corr_curve.append(average_corr)

    return corr_curve


def calculate_curves_per_window(window: np.ndarray):
    curve_elevation = calculate_1d_autocorrelation_curve(window, 0)
    curve_axial = calculate_1d_autocorrelation_curve(window, 1)
    curve_lateral = calculate_1d_autocorrelation_curve(window, 2)
    curves = np.array([curve_elevation, curve_axial, curve_lateral])

    return curves


def calculate_curves_per_window_ind_avg(window: np.ndarray):
    curve_elevation = calculate_1d_autocorrelation_curve_ind_avg(window, 0, 2)
    curve_axial = calculate_1d_autocorrelation_curve_ind_avg(window, 1, 0)
    curve_lateral = calculate_1d_autocorrelation_curve_ind_avg(window, 2, 0)
    curves = np.array([curve_elevation, curve_axial, curve_lateral])

    return curves


def calculate_correlation_curves_at_all_depths(window_shape: np.ndarray, depths_start_end: np.ndarray):
    """For each starting window depth, calculate each correlation curve"""
    return


def load_rf(dir_rf: Path) -> (np.ndarray, dict):
    list_rf = recon.get_sorted_list_mats(dir_rf, search_str='RF.mat')
    array_rf = recon.mat_list_to_rf_array(list_rf)
    params = recon.open_parameters(list_rf[0])

    return array_rf, params


def calc_corr_curves(rf_array: np.ndarray, window_params: dict) -> np.ndarray:
    return


def plot_curves(array_curves: np.ndarray, params_acq: dict, dir_output: Path, suffix_output: 'str'):
    return


def calc_plot_corr_curves(dir_rf: Path, window_params: dict, dir_output: Path=None, suffix_output: str=None):
    rf_array, params_acquisition = load_rf(dir_rf)
    curves = calc_corr_curves(rf_array, window_params)
    plot_curves(curves, params_acquisition, dir_output, suffix_output)



