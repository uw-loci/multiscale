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

import javabridge
import bioformats as bf
import SimpleITK as sitk


def idx_dictionary():
    """Map the polarization state inputs and output states to the z slice from the channel"""
    idx_of_outputs = {
        'Hout': [0, 6, 9, 14],
        'Bout': [1, 7, 8, 15],
        'Pout': [2, 5, 10, 13],
        'Vout': [3, 4, 11, 12],
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


def find_transforms(path_img):






def register_views(path_img):



javabridge.start_vm(class_path=bf.JARS)

path = r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_32x\1367 slide 5.czi'

with bf.ImageReader(path) as reader:
    test = reader.read()
    img = sitk.GetImageFromArray(test)
    print('hello')

javabridge.kill_vm()


