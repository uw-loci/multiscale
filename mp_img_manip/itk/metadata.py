# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:40:25 2018

@author: mpinkert
"""

import mp_img_manip.bulk_img_processing as blk

import SimpleITK as sitk
import os
import numpy as np


def setup_image(image_path, return_image=True, return_rotation=False):
    """Set up the image spacing and optionally the registration origin
    
    This function is necessary because ITK cannot save in microns, making
    external metadata necessary.  It references, or creates, a csv file to
    handle this metadata
    
    Inputs:
    image_path -- The path to the image being setup
    setup_origin -- Set values for the origin or leaves at 0,0
    return_image -- Return the whole setup image
    return_spacing -- Return the spacing values
    
    Outputs:
    image -- The setup image if return_image is True
    spacing -- The spacing of the image if return_spacing is True
    
    """

    parameters = get_image_parameters(image_path)

    if return_image:
        image = sitk.ReadImage(str(image_path))

        if len(image.GetSpacing()) > 2:
            array = sitk.GetArrayFromImage(image)
            array_2d = np.average(array, 0)
            array_2d[array_2d > 230] = 0
            image = sitk.GetImageFromArray(array_2d)

        image.SetSpacing(parameters[0])
        image.SetOrigin(parameters[1])

        if return_rotation:
            return image, parameters[2]
        else:
            return image
    elif return_rotation:
        return parameters[2]
            

def get_image_parameters(image_path, return_spacing=True, return_origin=True,
                         return_rotation=True):
    file_path = str(image_path.parent) + '/Image Parameters.csv'

    image_parameters = blk.read_write_pandas_row(
            str(file_path), str(image_path.name),
            'Image', ['Spacing', 'X Origin', 'Y Origin', 'Rotation'])

    spacing = [float(image_parameters['Spacing']),
               float(image_parameters['Spacing'])]
    
    origin = [float(image_parameters['X Origin']),
              float(image_parameters['Y Origin'])]
    
    rotation = float(image_parameters['Rotation'])
    
    returns = []
    if return_spacing:
        returns.append(spacing)
        
    if return_origin:
        returns.append(origin)
    
    if return_rotation:
        returns.append(rotation)

    return returns
    
    
def write_image_parameters(image_path, spacing, origin, rotation):
    """Write down the spacing and origin of an image file to csv metadata"""
    
    (output_dir, image_name) = os.path.split(image_path)
    
    file_path = output_dir + '/Image Parameters.csv'
    
    column_labels = ['Spacing', 'X Origin', 'Y Origin', 'Rotation']
    
    column_values = [spacing[0], origin[0], origin[1], rotation]
    
    blk.write_pandas_row(file_path,image_name,column_values,
                         'Image',column_labels)    