# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import mp_img_manip.itk.registration as reg
import mp_img_manip.itk.transform as trans
import mp_img_manip.itk.process as proc
import mp_img_manip.dir_dictionary as dird
import mp_img_manip.polarimetry as pol

def perform_registrations(skip_existing_images=True):
    """Overall script to perform both mmp and shg registrations
    
    Produces images at each step 
    00 - Polscope intensity to retardance
    01 - Resized images 
    02 - Registered images
    03 - Registered images maskped to MMP boundaries"""
    
    dir_dict = dird.create_dictionary()
    
    pol.bulk_intensity_to_retardance(dir_dict['ps_large'], 
                                     dir_dict['ps_large_ret'],
                                     'PS_Large_Ret',
                                     skip_existing_images=skip_existing_images)
#      
    resize_images(dir_dict, skip_existing_images=skip_existing_images)
#
    register_small_images(dir_dict, skip_existing_images)
#    mask_small_images(dir_dict, skip_existing_images=skip_existing_images)

#    apply_transform_to_large_images(dir_dict, skip_existing_images=skip_existing_images)
#    mask_large_images(dir_dict, skip_existing_images=skip_existing_images)
#    make_eightbit_images(dir_dict, skip_existing_images=skip_existing_images)
    
    

def resize_images(dir_dict, target_spacing=5, skip_existing_images=False):
    """Resize the small MMP to ~ PS resolution.
        Resize the large PS images to ~ small MMP resolution
        Resize the large SHG images to ~ small MMP resolution"""
        
#    trans.bulk_resize_image(dir_dict["ster_hr_small"],
#                           dir_dict["ps_large_ret"],dir_dict["ps_small"],
#                           'PS_Small')
#    
#    trans.bulk_resize_image(dir_dict["ster_hr_small"],
#                           dir_dict["shg_large"],dir_dict["shg_small"],
#                           'SHG_Small')
#    
#    trans.bulk_resize_image(dir_dict["ps_large"],
#                           dir_dict["ster_hr_small"],dir_dict["ster_hr_large"],
#                           'SterHR_Large')    
        

    trans.bulk_resize_to_target(
            dir_dict["ps_large_ret"], dir_dict["ps_small"], 'PS_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)
    
    trans.bulk_resize_to_target(
            dir_dict["shg_large"], dir_dict["shg_small"], 'SHG_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)
            
    trans.bulk_resize_to_target(
            dir_dict["ster_hr_large"], dir_dict["ster_hr_small"], 'SterHR_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)    
    
    trans.bulk_resize_to_target(
            dir_dict["ster_lr_large"], dir_dict["ster_lr_small"], 'SterLR_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)    


def register_small_images(dir_dict, skip_existing_images=False):
    """Register the small MMP to small PS.  Small SHG to small PS"""
    reg.bulk_supervised_register_images(
            dir_dict["ps_small"], 
            dir_dict["ster_lr_small"], 
            dir_dict["ster_lr_small_reg"], 'SterLR_Small_Reg',
            skip_existing_images=skip_existing_images)
    
    reg.bulk_supervised_register_images(
            dir_dict["ps_small"], dir_dict["shg_small"],
            dir_dict["shg_small_reg"], 'SHG_Small_Reg',
            skip_existing_images=skip_existing_images)


def mask_small_images(dir_dict, skip_existing_images=False):
    """Set all pixels outside the MMP ROI as 0 for PS and SHG"""
    proc.bulk_apply_mask(dir_dict["ps_small"], dir_dict['ster_lr_small_reg'],
                         dir_dict["ps_small_mask"], 'PS_Small_Masked',
                         skip_existing_images=skip_existing_images)
    
    proc.bulk_apply_mask(dir_dict["shg_small_reg"], dir_dict['ster_lr_small_reg'],
                         dir_dict["shg_small_mask"], 'SHG_Small_Masked',
                         skip_existing_images=skip_existing_images)

    return


def apply_transform_to_large_images(dir_dict, skip_existing_images=False):
    trans.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["ster_lr_large"],
                              dir_dict["ster_lr_small_reg"],
                              dir_dict["ster_lr_large_reg"],'SterLR_Large_Reg',
                              skip_existing_images=skip_existing_images)
    
    trans.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["shg_large"],
                              dir_dict["shg_small_reg"],
                              dir_dict["shg_large_reg"], 'SHG_Large_Reg',
                              skip_existing_images=skip_existing_images)


def mask_large_images(dir_dict, skip_existing_images=False):
    """Set all pixels outside the MMP ROI as 0 for PS and SHG"""
#    proc.bulk_apply_mask(dir_dict["ps_large"], dir_dict['ster_lr_large_reg'],
#                         dir_dict["ps_large_mask"], 'PS_Large_Masked')
#    
#    proc.bulk_apply_mask(dir_dict["shg_large_reg"], dir_dict['ster_lr_large_reg'],
#                         dir_dict["shg_large_mask"], 'SHG_Large_Masked')
#    
    
    proc.bulk_threshold(
            dir_dict['ster_lr_large_reg'], dir_dict['ster_lr_large_mask'],
            'SterLR_Large_Mask',
            skip_existing_images=skip_existing_images)
    
    proc.bulk_threshold(
            dir_dict['ster_lr_small_reg'], dir_dict['ster_lr_small_mask'],
            'SterLR_Small_Mask',
            skip_existing_images)
    
    return

def make_eightbit_images(dir_dict):
    proc.bulk_convert_to_eightbit(dir_dict["ps_large_mask"],
                                  dir_dict['ps_large_8bit'],
                                  'PS_Large_8Bit')

    proc.bulk_convert_to_eightbit(dir_dict["shg_large_mask"],
                                  dir_dict['shg_large_8bit'],
                                  'SHG_Large_8Bit')
    
    proc.bulk_convert_to_eightbit(dir_dict["ster_hr_large_reg"],
                                  dir_dict['ster_hr_large_8bit'],
                                  'SterHR_Large_8Bit')
    
    proc.bulk_convert_to_eightbit(dir_dict["ster_lr_large_reg"],
                                  dir_dict['ster_lr_large_8bit'],
                                  'SterLR_Large_8Bit')

    proc.bulk_convert_to_eightbit(dir_dict["ps_small_mask"],
                                  dir_dict['ps_small_8bit'],
                                  'PS_Small_8Bit')

    proc.bulk_convert_to_eightbit(dir_dict["shg_small_mask"],
                                  dir_dict['shg_small_8bit'],
                                  'SHG_Small_8Bit')
    
    proc.bulk_convert_to_eightbit(dir_dict["ster_hr_small_reg"],
                                  dir_dict['ster_hr_small_8bit'],
                                  'SterHR_Small_8Bit')
    
    proc.bulk_convert_to_eightbit(dir_dict["ster_lr_small_reg"],
                                  dir_dict['ster_lr_small_8bit'],
                                  'SterLR_Small_8Bit')

perform_registrations()

    
