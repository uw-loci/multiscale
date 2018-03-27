# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 10:06:55 2018

@author: mpinkert
"""
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itk.metadata as meta

import SimpleITK as sitk
import numpy as np
import os

def overlay_images(fixed_image, moving_image, alpha = 0.7):
    """Create a numpy array that is an 8bit combination of two images
    
    Inputs:
    fixed_image -- Image one, using registration nomenclature
    moving_image -- Image two, using registration nomeclature
    alpha -- degree of weighting towards the moving image
    
    """
    
    fixed_array = sitk.GetArrayFromImage(fixed_image)
    fixed_normalized = (fixed_array - np.amin(fixed_array))/(
            np.amax(fixed_array) + np.amin(fixed_array))

    try: #Post-registration
        moving_array = sitk.GetArrayFromImage(moving_image)
        moving_normalized = (moving_array - np.amin(moving_array))/(
                np.amax(moving_array)+np.amin(moving_array))
        
        combined_array = ((1.0 - alpha)*fixed_normalized 
                          + alpha*moving_normalized)
        
        return combined_array
    
    except: #Pre-registration
        initial_transform = sitk.Similarity2DTransform()
        moving_resampled = sitk.Resample(moving_image, fixed_image, 
                                         initial_transform, sitk.sitkLinear,
                                         0.0, moving_image.GetPixelID())
        
        moving_array = sitk.GetArrayFromImage(moving_resampled)
        moving_normalized = (moving_array - np.amin(moving_array))/(
                np.amax(moving_array)+np.amin(moving_array))

        combined_array = ((1.0 - alpha)*fixed_normalized 
                          + alpha*moving_normalized)
        return combined_array    
    

def bulk_apply_mask(image_dir, mask_dir,
                    output_dir, output_suffix):
    
    (image_path_list, mask_path_list) = blk.find_shared_images(
            image_dir, mask_dir)
    
    for i in range(0, np.size(image_path_list)):
        
        image = meta.setup_image(image_path_list[i])
        mask = meta.setup_image(mask_path_list[i]) > 0
        
        print('Masking ' + os.path.basename(image_path_list[i]) + ' with '
          + os.path.basename(mask_path_list[i]))
        
        masked_image = sitk.Mask(image,mask)
        
        masked_path = blk.create_new_image_path(
                image_path_list[i], output_dir, output_suffix)
        
        sitk.WriteImage(masked_image, masked_path)
                
    