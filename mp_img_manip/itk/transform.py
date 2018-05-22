# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:39:34 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itk.metadata as meta
import mp_img_manip.utility_functions as util

import SimpleITK as sitk
import numpy as np
import os
import math
from pathlib import Path


def write_transform(registered_path, transform, metric, stop):
    """Write affine transform parameters to a csv file"""
    (output_dir, image_name) = os.path.split(registered_path)

    file_path = output_dir + '/Transforms.csv'

    column_labels = ('Matrix Top Left', 'Matrix Top Right',
                     'Matrix Bottom Left', 'Matrix Bottom Right',
                     'X Translation', 'Y Translation',
                     'Mutual Information', 'Stop Condition')

    column_values = list(transform.GetParameters())
    column_values.append(metric)
    column_values.append(stop)

    blk.write_pandas_row(file_path, image_name, column_values,
                         'Image', column_labels)


def apply_transform(fixed_path, moving_path, reference_path,
                    transform_path=None):

    fixed_image = meta.setup_image(fixed_path)
    moving_image = meta.setup_image(moving_path)

    print('Applying transform onto {0} based on transform on {1}'.format(
        moving_path.name,
        reference_path.name))

    transform_path = os.path.join(reference_path.folder, 'Transforms.csv')

    transform_params = blk.read_pandas_row(transform_path,
                                           reference_path.name, 'Image')

    transform = sitk.AffineTransform(2)
    matrix = [transform_params['Matrix Top Left'],
              transform_params['Matrix Top Right'],
              transform_params['Matrix Bottom Left'],
              transform_params['Matrix Bottom Right']]

    transform.SetMatrix(matrix)
    transform.SetTranslation([transform_params['X Translation'],
                              transform_params['Y Translation']])

    return sitk.Resample(moving_image, fixed_image, transform,
                         sitk.sitkLinear, 0.0, moving_image.GetPixelID())


def bulk_apply_transform(fixed_dir, moving_dir, transform_dir,
                         output_dir, output_suffix):

    fixed_paths, moving_paths, transform_paths = blk.find_bulk_shared_images(
        [fixed_dir, moving_dir, transform_dir])

    for i in range(0, np.size(fixed_paths)):

        registered_image = apply_transform(fixed_paths[i],
                                           moving_paths[i],
                                           transform_paths[i])

        registered_path = blk.create_new_image_path(moving_paths[i],
                                                    output_dir,
                                                    output_suffix)

        sitk.WriteImage(registered_image, registered_path)
        meta.write_image_parameters(registered_path,
                                    registered_image.GetSpacing(),
                                    registered_image.GetOrigin())

    return


#def apply_transform_to_whole_folder(fixed_dir, moving_dir_list)


def resize_image(image_path, current_spacing, target_spacing):
    """Resize an image by an integer factor towards target spacing"""
    itk_image = meta.setup_image(image_path,
                                 return_image=True, print_parameters=False)

    image_name = os.path.basename(image_path)

    if current_spacing < target_spacing:
        scale = math.floor(target_spacing/current_spacing)
        end_res = current_spacing*scale

        resized_image = sitk.Shrink(itk_image, [scale, scale])
        resized_image.SetSpacing([end_res, end_res])
        resized_image.SetOrigin(itk_image.GetOrigin())

    elif current_spacing > target_spacing:
        scale = math.floor(current_spacing/target_spacing)
        end_res = current_spacing/scale

        resized_image = sitk.Expand(itk_image,[scale, scale])
        resized_image.SetSpacing([end_res, end_res])
        resized_image.SetOrigin(itk_image.GetOrigin())

    print('Resizing ' + image_name + ' from '
          + str(current_spacing) + ' to ' + str(end_res)
          + ' (Target = ' + str(target_spacing) + ')')

    return resized_image


def bulk_resize_image(fixed_dir, moving_dir, output_dir, output_suffix):
    """Resize multiple images to corresponding reference size"""
    (fixed_image_path_list, moving_image_path_list) = blk.find_shared_images(
        fixed_dir, moving_dir)

    for i in range(0, np.size(fixed_image_path_list)):
        current_spacing = meta.setup_image(moving_image_path_list[i],
                                           return_image = False,
                                           return_spacing=True)[0]

        target_spacing = meta.setup_image(fixed_image_path_list[i],
                                          return_image = False,
                                          return_spacing=True)[0]

        resized_image = resize_image(moving_image_path_list[i],
                                     current_spacing, target_spacing)

        resized_path = blk.create_new_image_path(moving_image_path_list[i],
                                                 output_dir, output_suffix)

        sitk.WriteImage(resized_image, resized_path)
        meta.write_image_parameters(resized_path,
                                    resized_image.GetSpacing(),
                                    resized_image.GetOrigin())


#def crop_to_nonzero_boundary(image_path, output_dir, output_suffix,
#                             reference_path = None):
#    """Not yet implemented"""
#    
#    return
#
#
#def bulk_crop_to_nonzero_boundary(image_dir, output_dir, output_suffix,
#                                  reference_dir = None):
#    return