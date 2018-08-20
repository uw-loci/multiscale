"""Script for manipulating ultrasound data for the LINK project
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
    bmode = np.power(env, 2)

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


def index_from_file_path(path_file: Path) -> int:
    """Get the image index from filename formatted It-index.mat"""
    match = re.search(r'It-\d*', path_file.stem)
    index = int(match.group()[3:]) - 1
    return index


def get_idx_img_z(idx_raw: int, num_xy: np.ndarray, num_imgs: int) -> [int, int]:
    z_size = num_imgs/num_xy[0]
    img = int(idx_raw / z_size)
    z = np.mod(idx_raw, z_size)
    return int(img), int(z)


def assemble_4d_image(list_mats: list, num_xy: np.ndarray) -> np.ndarray:
    """Compile US .mats into separate 3d images"""
    image_shape = np.shape(open_iq(list_mats[0]))
    num_imgs = len(list_mats)

    array_4d_im_z_yx = np.zeros([num_xy[0], num_xy[1], image_shape[0], image_shape[1]])

    # todo: vectorize this loop
    for path in list_mats:
        idx_raw = index_from_file_path(path)
        img, z = get_idx_img_z(idx_raw, num_xy, num_imgs)
        iq = open_iq(path)
        bmode = iq_to_bmode(iq)
        array_4d_im_z_yx[img, z, :, :] = bmode

    return array_4d_im_z_yx


def stitch_us_image(dir_mats: Path, path_pl: Path, dir_output: Path, name_output: str):
    list_mats = util.list_filetype_in_dir(dir_mats, 'mat')
    list_pos = read_position_list(path_pl)
    num_xy = count_xy_positions(list_pos)
    separate_images_4d = assemble_4d_image(list_mats, num_xy)

    for idx in range(num_xy[0]):
        path_output = Path(dir_output, name_output + '_' + str(idx) + '.tif')
        image = sitk.GetImageFromArray(separate_images_4d[idx])
        image_cast = sitk.Cast(image, sitk.sitkFloat32)
        sitk.WriteImage(image_cast, str(path_output))


dir_mats = Path("C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\PhantomGrid-TopLeftStart\\Run-2")
path_pl = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\US Phantom grid 2018-08-17.pos')
dir_output = Path('C:\\Users\\mpinkert\\Box\\Research\\LINK\\Ultrasound\\Ultrasound Data\\2018-08-17\\')
name_output = 'FirstImage3D'
stitch_us_image(dir_mats, path_pl, dir_output, name_output)


