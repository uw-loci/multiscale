"""
Mueller matrix polarimetry takes many different images of the same
sample using different input and output polarizations.  Changing the
output polarization on the instrument we are using changes the
optical path, and thus shifts the images.

This script is intended to register the images onto each other and
find a universal transform so that it can be applied to all future
images from the same source.  This will let us get better results with
the final Mueller image.
"""
import mp_img_manip.itk.registration as reg

import javabridge
import bioformats as bf
import SimpleITK as sitk
from pathlib import Path
import os
import pandas as pd

import mp_img_manip.itk.transform as tran
import mp_img_manip.utility_functions as util


def czi_timepoint_to_sitk_image(path_file, position, resolution):
        """
        Open a timepoint from a czi image and make it into an ITK image
        
        :param path_file: Path to the czi file
        :param position: Timepoint to open
        :param resolution: Resolution of the czi image in microns
        :return: A SimpleITK image made from the timepoint
        """
        array = bf.load_image(str(path_file), t=position)
        image = sitk.GetImageFromArray(array)
        image.SetSpacing([resolution, resolution])
        
        return image


def idx_dictionary():
    """Map the polarization state inputs and output states to the t slice from the channel"""
    idx_of_outputs = {
        'Hout': [0, 6, 9, 14],
        'Bout': [1, 7, 8, 15],
        'Pout': [2, 5, 10, 13],
        'Vout': [4, 3, 11, 12],
        'Rout': [18, 19, 20, 17],
        'Lout': [23, 22, 21, 16]}

    idx_of_inputs = {
        'Hin': [0, 1, 2, 3, 18, 23],
        'Pin': [6, 7, 5, 19, 22],
        'Vin': [9, 8, 10, 11, 20, 21],
        'Rin': [14, 15, 13, 12, 17, 16]
    }

    idx_dict = {'Outputs': idx_of_outputs, 'Inputs': idx_of_inputs}

    return idx_dict


def find_transforms(path_img: Path, resolution, registration_method, skip_finished_transforms=True):
    idx_dict = idx_dictionary()
    slices_to_register = []
    keys = []
    dict_outputs = idx_dict['Outputs']
    for key in dict_outputs:
        keys.append(key)
        slices_to_register.append(dict_outputs[key][0])

    fixed_img = czi_timepoint_to_sitk_image(path_img, slices_to_register[0], resolution)

    for idx in range(1, len(slices_to_register)):
        registered_path = Path(path_img.parent, keys[idx])

        if skip_finished_transforms:
            (output_dir, image_name) = os.path.split(registered_path)
            file_path = output_dir + '/Transforms.csv'
            df_transforms = pd.read_csv(file_path, index_col=0)
            if image_name in df_transforms.index:
                continue

        print('Registering {0} to {1}'.format(keys[idx], keys[0]))

        moving_img = czi_timepoint_to_sitk_image(path_img, slices_to_register[idx], resolution)

        registered_img, origin, transform, metric, stop, rotation = reg.supervised_register_images(
            fixed_img, moving_img, registration_method=registration_method
        )

        tran.write_transform(registered_path, origin, transform, metric, stop, rotation)


javabridge.start_vm(class_path=bf.JARS)

mlr_path = Path(r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_32x\1367 slide 5.czi')
mhr_path = Path(r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_80x\1045- slide 1.czi')
mlr_resolution = 2.016
mhr_resolution = 0.81

registration_method = reg.define_registration_method(scale=1, learning_rate=5, iterations=300)

find_transforms(mlr_path, mlr_resolution, registration_method)
find_transforms(mhr_path, mlr_resolution, registration_method)


javabridge.kill_vm()


