"""Script for reconstructing ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import scipy.io as sio
from pathlib import Path
import numpy as np
import mp_img_manip.utility_functions as util
import re
import SimpleITK as sitk


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
    """Convert complex IQ data into bmode through squared transform"""
    env = np.abs(array_iq)
    bmode = np.log10(env+1)

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


def count_xy_positions(list_pos: list) -> np.ndarray:
    """Determine how many unique X and Y positions the position list holds, as well as the physical separation in x"""
    array_pos = np.array(list_pos)
    unique = np.unique(array_pos[:, 0], return_counts=True)
    num_xy = np.array([len(unique[0]), unique[1][0]])

    if len(unique[0]) > 1:
        x_sep = unique[0][1] - unique[0][0]
    else:
        x_sep = 0

    return num_xy, x_sep


def index_from_file_path(path_file: Path) -> int:
    """Get the image index from filename formatted It-index.mat"""
    match = re.search(r'It-\d*', path_file.stem)
    index = int(match.group()[3:]) - 1
    return index


def get_sorted_list_mats(dir_mats: Path) -> list:
    unsorted =  util.list_filetype_in_dir(dir_mats, 'mat')
    list_mats_sorted = sorted(unsorted, key=index_from_file_path)
    return list_mats_sorted


def get_idx_img_z(idx_raw: int, num_xy: np.ndarray, num_imgs: int) -> [int, int]:
    """Extract indexes for the 3D image and the elevational Z position of a mat file"""
    z_size = num_imgs/num_xy[0]
    idx_img = int(idx_raw / z_size)
    idx_z = np.mod(idx_raw, z_size)
    return int(idx_img), int(idx_z)


def assemble_4d_image(list_mats: list, num_xy: np.ndarray) -> np.ndarray:
    """Compile IQ Data US .mats into separate 3d images"""
    image_shape = np.shape(open_iq(list_mats[0]))
    num_imgs = len(list_mats)

    array_4d_im_z_yx = np.zeros([num_xy[0], num_xy[1], image_shape[0], image_shape[1]])

    # todo: vectorize this loop
    for path in list_mats:
        iq = open_iq(path)
        bmode = iq_to_bmode(iq)

        idx_raw = index_from_file_path(path)
        idx_img, idx_z = get_idx_img_z(idx_raw, num_xy, num_imgs)

        array_4d_im_z_yx[idx_img, idx_z, :, :] = bmode

    return array_4d_im_z_yx


def calculate_percent_overlap(x_sep: float) -> int:
    """Calculate the percentage overlap between X images"""
    percent_sep = int(100 - 100*(x_sep / 12800))
    return percent_sep




def stitch_us_image(dir_mats: Path, path_pl: Path, dir_output: Path, name_output: str):
    """Stitch together a directory of US images taken using micromanager/verasonics into a 3D composite"""
    list_mats = get_sorted_list_mats(dir_mats)
    list_pos = read_position_list(path_pl)
    num_xy, x_sep = count_xy_positions(list_pos)
    separate_images_4d = assemble_4d_image(list_mats, num_xy)

    percent_overlap = calculate_percent_overlap(x_sep)

    for idx in range(num_xy[0]):
        path_output = Path(dir_output, name_output + '_Overlap-' + str(percent_overlap) + '_' + str(idx) + '.tif')
        image = sitk.GetImageFromArray(separate_images_4d[idx])
        image_cast = sitk.Cast(image, sitk.sitkFloat32)
        sitk.WriteImage(image_cast, str(path_output))


dir_mats = Path("C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\PhantomGrid-TopLeftStart\\Run-2")
path_pl = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\US Phantom grid 2018-08-17.pos')
dir_output = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\')
name_output = 'FirstImage3D'
stitch_us_image(dir_mats, path_pl, dir_output, name_output)


