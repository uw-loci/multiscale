# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:39:34 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itk.metadata as meta

import SimpleITK as sitk
import numpy as np
import os
import math
from pathlib import Path


def write_transform(registered_path, transform):
        transform_path = Path(registered_path.parent, registered_path.stem + '.tfm')
        sitk.WriteTransform(transform, str(transform_path))
        

def apply_transform(fixed_image: sitk.Image, moving_image: sitk.Image, transform_path):
        transform = sitk.ReadTransform(str(transform_path))
        return sitk.Resample(moving_image, fixed_image, transform,
                             sitk.sitkLinear, 0.0, moving_image.GetPixelID())
        

def write_transform_pandas(registered_path, origin, transform, metric, stop, rotation):
        """Write affine transform parameters to a csv file"""
        (output_dir, image_name) = os.path.split(registered_path)
        
        file_path = output_dir + '/Transforms.csv'
        
        column_labels = ('Matrix Top Left', 'Matrix Top Right',
                         'Matrix Bottom Left', 'Matrix Bottom Right',
                         'X Translation', 'Y Translation',
                         'Mutual Information', 'Stop Condition',
                         'X Origin', 'Y Origin', 'Rotation')
        
        column_values = list(transform.GetParameters())
        column_values.append(metric)
        column_values.append(stop)
        column_values.append(origin[0])
        column_values.append(origin[1])
        column_values.append(rotation)
        
        blk.write_pandas_row(file_path, image_name, column_values,
                             'Image', column_labels)


def apply_transform_pandas(fixed_image: sitk.Image, moving_image: sitk.Image, reference_path, index=None):
        
        transform_path = os.path.join(reference_path.parent, 'Transforms.csv')
        
        if index is None:
                transform_params = blk.read_pandas_row(transform_path, reference_path.name, 'Image')
        else:
                transform_params = blk.read_pandas_row(transform_path, index, 'Image')
        
        transform = sitk.AffineTransform(2)
        
        transform.Rotate(0, 1, transform_params['Rotation'], pre=True)
        
        matrix = [transform_params['Matrix Top Left'],
                  transform_params['Matrix Top Right'],
                  transform_params['Matrix Bottom Left'],
                  transform_params['Matrix Bottom Right']]
        
        transform.SetMatrix(matrix)
        transform.SetTranslation([transform_params['X Translation'],
                                  transform_params['Y Translation']])
        
        origin = (int(transform_params['X Origin']),
                  int(transform_params['Y Origin']))
        moving_image.SetOrigin(origin)
        
        return sitk.Resample(moving_image, fixed_image, transform,
                             sitk.sitkLinear, 0.0, moving_image.GetPixelID())


def bulk_apply_transform(fixed_dir, moving_dir, transform_dir,
                         output_dir, output_suffix,
                         skip_existing_images=False):
        
        fixed_paths, moving_paths, reference_paths = blk.find_bulk_shared_images(
                [fixed_dir, moving_dir, transform_dir])
        
        for i in range(0, np.size(fixed_paths)):
                registered_path = blk.create_new_image_path(moving_paths[i],
                                                            output_dir,
                                                            output_suffix)
                
                if registered_path.exists() and skip_existing_images:
                        continue
                
                fixed_image = meta.setup_image_from_csv(fixed_paths[i])
                moving_image = meta.setup_image_from_csv(moving_paths[i])
                
                print('\nApplying transform onto {0} based on transform on {1}'.format(
                        str(moving_paths[i].name),
                        str(reference_paths[i].name)))
                
                registered_image = apply_transform_pandas(fixed_image,
                                                          moving_image[i],
                                                          reference_paths[i])
                
                sitk.WriteImage(registered_image, str(registered_path))
                meta.write_image_parameters(registered_path,
                                            registered_image.GetSpacing(),
                                            registered_image.GetOrigin(),
                                            0)
        
        return


def resize_image(itk_image, current_spacing, target_spacing):
        """Resize an image by an integer factor towards target spacing"""
        
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
        
        return resized_image


def bulk_resize_image(fixed_dir, moving_dir, output_dir, output_suffix,
                      skip_existing_images=False):
        """Resize multiple images to corresponding reference size"""
        (fixed_image_path_list, moving_image_path_list) = blk.find_shared_images(
                fixed_dir, moving_dir)
        
        for i in range(0, np.size(fixed_image_path_list)):
                resized_path = blk.create_new_image_path(moving_image_path_list[i],
                                                         output_dir, output_suffix)
                if resized_path.exists() and skip_existing_images:
                        continue
                
                current_spacing = meta.get_image_parameters(
                        moving_image_path_list[i],
                        return_origin=True,
                        return_spacing=True)[0]
                
                target_spacing = meta.get_image_parameters(
                        fixed_image_path_list[i],
                        return_origin=True,
                        return_spacing=True)[0]
                
                resized_image = resize_image(moving_image_path_list[i],
                                             current_spacing, target_spacing)
                
                sitk.WriteImage(resized_image, str(resized_path))
                meta.write_image_parameters(resized_path,
                                            resized_image.GetSpacing(),
                                            resized_image.GetOrigin())


def bulk_resize_to_target(image_dir, output_dir, output_suffix,
                          target_spacing,
                          skip_existing_images=False):
        
        image_name_list = [
                Path(f) for f in os.listdir(image_dir) if f.endswith('.tif')]
        
        for i in range(0, np.size(image_name_list)):
                image_path = Path(image_dir, image_name_list[i])
                
                resized_path = blk.create_new_image_path(image_path,
                                                         output_dir, output_suffix)
                if resized_path.exists() and skip_existing_images:
                        continue
                
                current_spacing = meta.get_image_parameters(image_path, return_origin=False, return_spacing=True)[0][0]
                itk_image = meta.setup_image_from_csv(image_path)
                image_name = os.path.basename(image_path)
                print('\nResizing ' + image_name + ' from '
                      + str(current_spacing) + ' to target spacing ' + str(target_spacing) + ')')
                
                resized_image = resize_image(itk_image,
                                             current_spacing, target_spacing)
                
                sitk.WriteImage(resized_image, str(resized_path))
                meta.write_image_parameters(resized_path,
                                            resized_image.GetSpacing(),
                                            resized_image.GetOrigin(),
                                            0)

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
def define_transform(type_of_transform: str='affine', rotation: np.double=0) -> sitk.Transform:
        
        deg_to_rad = 2*np.pi/360
        angle = rotation*deg_to_rad
        
        if type_of_transform == 'euler':
                transform = sitk.Euler2DTransform()
                transform.SetAngle(angle)
        elif type_of_transform == 'affine':
                transform = sitk.AffineTransform(2)
                transform.Rotate(0, 1, angle, pre=True)
        else:
                raise('{0} registration has not been implemented yet'.format(type_of_transform))
        
        return transform