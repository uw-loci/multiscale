# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:39:34 2018

@author: mpinkert
"""
import mp_image_manip.bulk_image_processing as blk
import mp_image_manip.itk.metadata as meta 

import SimpleITK as sitk
import numpy as np
import os
import math

def write_transform(registered_path,transform, metric, stop):
    
    (output_dir, image_name) = os.path.split(registered_path)
    
    file_path = output_dir + '/Transforms.csv'
    
    column_labels = ('Matrix Top Left', 'Matrix Top Right',
                    'Matrix Bottom Left', 'Matrix Bottom Right',
                    'X Translation', 'Y Translation',
                    'Mutual Information', 'Stop Condition')
    
    column_values = transform.GetParameters()
    column_values.append(metric)
    column_values.append(stop)
    
    blk.write_pandas_row(file_path,image_name,column_values,
                         'Image',column_labels)
    
    
def resize_image(image_path, output_suffix, current_spacing, target_spacing):
    itkImg = meta.setup_image(image_path, return_image = True)
    
    scale = math.floor(target_spacing/current_spacing)
    endRes = current_spacing*scale
    
    if current_spacing < target_spacing:      
        shrunk = sitk.Shrink(itkImg,[scale,scale])
        shrunk.SetSpacing([endRes,endRes])
        return shrunk
    
    elif current_spacing > target_spacing:
        expand = sitk.Expand(itkImg,[scale,scale])
        expand.SetSpacing([endRes,endRes])
        return expand
    
    
def bulk_resize_image(fixed_dir, moving_dir, output_dir, output_suffix):
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
                                     output_suffix,
                                     current_spacing,target_spacing)
        
        resized_path = blk.create_new_image_path(moving_image_path_list[i],
                                                 output_dir, output_suffix)

        sitk.WriteImage(resized_image,resized_path)
        meta.write_image_parameters(resized_path,
                               resized_image.GetSpacing(),
                               resized_image.GetOrigin())
        
def apply_transform(fixed_path, moving_path, transform):
    
    return

def bulk_apply_transform(fixed_dir, moving_dir, output_dir,
                         transform_dir,
                         output_suffix,):
    return