# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import os
import mp_img_manip.itk.registration as reg
import mp_img_manip.itk.transform as trans



def perform_registrations():
    """Overall script to perform both mmp and shg registrations
    
    Produces images at each step 
    
    01 - Resized images 
    02 - Registered images
    03 - Registered images maskped to MMP boundaries"""
    
    dir_dict = create_dictionary()
      
    resize_images(dir_dict)

    register_small_images(dir_dict)
    mask_small_images(dir_dict)

    apply_transform_to_large_images(dir_dict)
    mask_large_images(dir_dict)
    
    

def create_dictionary(
        base_dir = os.path.normpath('F:\Box Sync\Research\Polarimetry'),
        prep_dir = '02 - Python prepped images',
        resize_dir = '03 - Mid-python analysis images\\01 - Resizing images',
        reg_dir = '03 - Mid-python analysis images\\02 - Registered images',
        mask_dir = '03 - Mid-python analysis images\\02 - Cropped images'):
    
    
    dir_dict = {
    "ps_large" : os.path.join(base_dir, prep_dir, 'PS_Large'),
    "mmp_small" : os.path.join(base_dir, prep_dir, 'MMP_Small'),
    "shg_large" : os.path.join(base_dir, prep_dir, 'SHG_Large'),
    
    "ps_small" : os.path.join(base_dir,resize_dir,'PS_Small'),
    "shg_small" : os.path.join(base_dir,resize_dir,'SHG_Small'),
    "mmp_large" : os.path.join(base_dir,resize_dir,'MMP_Large'),
                                
    "mmp_small_reg" : os.path.join(base_dir,reg_dir,'MMP_Small_Reg'),
    "shg_small_reg" : os.path.join(base_dir,reg_dir,'SHG_Small_Reg'),

    "mmp_large_reg" : os.path.join(base_dir,reg_dir,'MMP_Large_Reg'),
    "shg_large_reg" : os.path.join(base_dir,reg_dir,'SHG_Large_Reg_Crop'),

    "ps_small_mask" : os.path.join(base_dir,mask_dir,'PS_Small_Crop'),
    "mmp_small_mask" : os.path.join(base_dir,mask_dir,'MMP_Small_Reg_Crop'),
    "shg_small_mask" : os.path.join(base_dir,mask_dir,'SHG_Small_Reg_Crop'),

    "ps_large_mask" : os.path.join(base_dir,mask_dir,'PS_Large_Crop'),
    "mmp_large_mask" : os.path.join(base_dir,mask_dir,'MMP_Large_Reg_Crop'),
    "shg_large_mask" : os.path.join(base_dir,mask_dir,'SHG_Large_Reg_Crop')}

    return dir_dict    


def resize_images(dir_dict):
    """Resize the small MMP to ~ PS resolution.
        Resize the large PS images to ~ small MMP resolution
        Resize the large SHG images to ~ small MMP resolution"""
        
    trans.bulk_resize_image(dir_dict["mmp_small"],
                           dir_dict["ps_large"],dir_dict["ps_small"],
                           'PS_Small')
    
    trans.bulk_resize_image(dir_dict["ps_small"],
                           dir_dict["shg_large"],dir_dict["shg_small"],
                           'SHG_Small')
    
    trans.bulk_resize_image(dir_dict["ps_large"],
                           dir_dict["mmp_small"],dir_dict["mmp_large"],
                           'MMP_Large')    



def register_small_images(dir_dict):
    """Register the small MMP to small PS.  Small SHG to small PS"""
    reg.bulk_supervised_register_images(dir_dict["ps_small"],
                                         dir_dict["mmp_small"],
                                         dir_dict["mmp_small_reg"],
                                         'MMP_Small_Reg')
    
    reg.bulk_supervised_register_images(dir_dict["ps_small"],
                                         dir_dict["shg_small"],
                                         dir_dict["shg_small_reg"],
                                         'SHG_Small_Reg')


def mask_small_images(dir_dict):
    return


def apply_transform_to_large_images(dir_dict):
    reg.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["mmp_large"],
                              dir_dict["mmp_large_reg"],
                              dir_dict["mmp_small_reg"],
                              'MMP_Large_Reg')
    
    reg.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["shg_large"],
                              dir_dict["shg_large_reg"],
                              dir_dict["shg_small_reg"], 
                              'SHG_Large_Reg')


def mask_large_images(dir_dict):
    return




    
