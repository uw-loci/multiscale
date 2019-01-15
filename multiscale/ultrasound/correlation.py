"""Script for performing correlations/PSF calculations on ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import numpy as np
from pathlib import Path
import scipy.signal as sig
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

plt.ion()

import multiscale.ultrasound.reconstruction as recon


def define_correlation_window(params_acquisition: dict):
    """Define the window over which the correlation is calculated inside the frame"""
    
    params_window = dict({'Elevational size mm': 1,
                          'Lateral size mm': 1,
                          'Axial size mm': 1,
                          'Start of depth range mm': 6,
                          'End of depth range mm': 8,
                          'Depth step mm': 0.25})
    
    return params_window


def determine_window_sweep():
    """Define the range the window sweeps over within the frames"""
    return


def detrend_and_add_back_mean(array_im: np.ndarray, dim_detrend:int) -> np.ndarray:
    """Detrend along a dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """
    shape_array = np.shape(array_im)
    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    array_mean = np.mean(array_detrend, axis=dim_detrend)

    if dim_detrend is 2:  # lateral
        array_output = array_detrend + array_mean[:, :, None]
    elif dim_detrend is 1:  # axial
        array_output = array_detrend + np.reshape(array_mean, [shape_array[0], 1, shape_array[2]])
    elif dim_detrend is 0:  # elevation
        array_output = array_detrend + array_mean
    else:
        raise ValueError('Please enter a valid dimension (0, 1, or 2)')

    return array_output


def detrend_along_dimension(array_im: np.ndarray, dim_detrend: int) -> np.ndarray:
    """Detrend along a dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """
    
    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    return array_detrend


def detrend_and_subtract_mean(array_im: np.ndarray, dim_detrend: int) -> np.ndarray:
    """Detrend along a dimension, and subtract a mean of the detrend along another dimension

    axis 0 = elevation
    axis 1 = axial
    axis 2 = lateral
    """
    
    array_detrend = sig.detrend(array_im, axis=dim_detrend)
    array_mean = np.mean(array_detrend, dim_detrend)
    shape_array = np.shape(array_detrend)
    
    if dim_detrend is 2: # lateral
        array_detrend_avg = array_detrend - array_mean[:, :, None]
    elif dim_detrend is 1: # axial
        array_detrend_avg = array_detrend - np.reshape(array_mean, [shape_array[0], 1, shape_array[2]])
    elif dim_detrend is 0: # elevation
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
        if shift > 20:
            break
            
        corr_along_lines = np.apply_along_axis(calculate_1d_autocorrelation, dim_of_corr, window, shift)
        average_corr = np.mean(corr_along_lines)
        # if average_corr < threshold:
        #     corr_curve.append(average_corr)
        #     break
        
        corr_curve.append(average_corr)
    
    corr_curve = np.array(corr_curve)
    
    return corr_curve


def calculate_curves_per_window(window: np.ndarray) -> dict:
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
    
    curves = {'Elevational': curve_elevation, 'Axial': curve_axial, 'Lateral': curve_lateral}
    
    return curves


def calculate_correlation_curves_at_all_depths(window_shape: np.ndarray, depths_start_end: np.ndarray):
    """For each starting window depth, calculate each correlation curve"""
    return


def load_iq(dir_iq: Path) -> (np.ndarray, dict):
    list_iq = recon.get_sorted_list_mats(dir_iq, search_str='IQ.mat')
    array_iq, params = recon.mat_list_to_iq_array(list_iq)
    
    return array_iq, params


def load_rf(dir_rf:Path) -> (np.ndarray, dict):
    list_rf = recon.get_sorted_list_mats(dir_rf, search_str='RF.mat')
    array_rf, params = recon.mat_list_to_rf_array(list_rf)
    return array_rf, params


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


def calc_corr_curves(env_array: np.ndarray, params_window: dict, params_acq: dict) -> np.ndarray:
    idx_start = int(np.floor(params_window['Start of depth range mm'] / params_acq['Axial resolution']))
    idx_end = int(np.floor(params_window['End of depth range mm'] / params_acq['Axial resolution']))
    
    window = env_array[:, idx_start:idx_end]
    window_squared = detrend_and_square_window(window)
    
    curves = calculate_curves_per_window(window_squared)
    
    return curves


def plot_corr_curve(curve_1d: np.ndarray, axis: str, spacing: np.double):
    fig, ax = plt.subplots()
    
    position = np.array(range(len(curve_1d)))*spacing*1000
    
    func_interp = interp1d(position, curve_1d, kind='slinear')
    new_position = np.arange(0, position[len(position)-1], 1)
    new_curve = func_interp(new_position)
    
    ax.plot(position, curve_1d, 'o', new_position, new_curve, '-')
    ax.set_title(axis + ' autocorrelation')
    ax.set_xlabel('microns')
    ax.set_xlim([0, position[len(position)-1]])
    ax.set_ylim([0, 1])
    
    half_max_idx = np.where(new_curve < 0.5)[0][0]
    half_max_loc = new_position[half_max_idx]
    ticks = np.append(position, half_max_loc)
    ax.axvline(half_max_loc)
    
    ax.set_xticks(ticks)

    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.02)


def plot_single_curves(dict_curves: dict, params_acq: dict, dir_output: Path=None, suffix_output: str=''):
    
    for axis, curve in dict_curves.items():
        spacing = params_acq[axis + ' resolution']
        plot_corr_curve(curve, axis, spacing)
        
        if dir_output is not None:
            name_output = Path(dir_output, axis + '_' + suffix_output + '.png')
            plt.savefig(str(name_output))


def calc_plot_corr_curves(dir_iq: Path, dir_output: Path=None, suffix_output: str='', elevation_res: np.double=0.02):
    iq_array, params_acquisition = load_iq(dir_iq)
    env_array = iq_to_envelope(iq_array)
    
    # todo automate this calculation
    params_acquisition['Elevational resolution'] = elevation_res
    
    params_window = define_correlation_window(params_acquisition)
    curves = calc_corr_curves(env_array, params_window, params_acquisition)
    
    plot_single_curves(curves, params_acquisition, dir_output, suffix_output)
    
    return


def rf_to_envelope(rf_array):
    """Take the hilbert transform along the axial direction"""
    env = np.abs(sig.hilbert(rf_array, axis=1))
    return env


def process_rf_to_correlation(dir_rf: Path, dir_output: Path = None, suffix_output: str = '',
                              elevation_res: np.double = 0.01848):
    rf_array, params_acquisition = load_rf(dir_rf)
    rf_detrended = detrend_along_dimension(rf_array, 1)
    env_array = rf_to_envelope(rf_detrended)
    
    # todo automate this calculation
    params_acquisition['Elevational resolution'] = elevation_res
    
    params_window = define_correlation_window(params_acquisition)
    curves = calc_corr_curves(env_array, params_window, params_acquisition)
    
    plot_single_curves(curves, params_acquisition, dir_output, suffix_output)
    
    return


def bulk_plot_corr_curves(list_dirs: list, dir_output: Path=None, suffix_output: str='', elevation_res: np.double=0.02):
    
    for dir_iq in list_dirs:
        iq_array, params_acquisition = load_iq(dir_iq)
        env_array = iq_to_envelope(iq_array)
        
        # todo automate this calculation
        params_acquisition['Elevational resolution'] = elevation_res
        
        params_window = define_correlation_window(params_acquisition)
        curves = calc_corr_curves(env_array, params_window, params_acquisition)