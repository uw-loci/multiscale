"""Script for manipulating ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import scipy.io as sio
from pathlib import Path
import numpy as np
import imagej


def open_iq(path_iq: Path) -> np.ndarray:
    """Open a .mat that holds IQData from the Verasonics system

    Input:
    A pathlib Path to an .mat file holding an 'IQData' variable, which is an array of complex numbers

    Output:
    A numpy array of complex numbers
    """
    mat_iq = sio.loadmat(str(path_iq))
    array_iq = mat_iq['IQData']
    return array_iq


def iq_to_bmode(array_iq: np.ndarray) -> np.ndarray:
    """Convert complex IQ data into bmode through log10 transform"""
    env = np.abs(array_iq)
    bmode = np.log10(env)

    return bmode


def clean_position_text(dict_text: dict) -> list:
    """Convert a Micromanager acquired position file into a list of X, Y positions"""
    list_pos_raw = dict_text['POSITIONS']
    list_pos = [[row['DEVICES'][0]['X'], row['DEVICES'][0]['Y']]
                for row in list_pos_raw]

    return list_pos


def read_position_list(path_pl: Path) -> list:
    """Open a Micromanager acquired position file and return a list of X, Y positions"""
    with open(path_pl, 'r') as file_pos:
        text_pos = file_pos.read()
        dict_text = eval(text_pos)
        list_pos = clean_position_text(dict_text)

    return list_pos


def convert_physical_pos_to_pixels(list_pos: list) -> list:
    return


def count_xy_positions(list_pos: list) -> np.ndarray:
    array_pos = np.array(list_pos)
    unique = np.unique(array_pos[:, 0], return_counts=True)
    num_xy = np.array([len(unique[0]), unique[1][0]])

    return num_xy


def create_z_stack():
    return


def stitch_z_stacks():
    return


def stitch_us_image(dir_input, dir_output, output_name):
