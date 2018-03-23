# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import os
import mp_img_manip.itk.registration as reg
import mp_img_manip.itk.transform as trans
import mp_img_manip.itk.process as proc
import mp_img_manip.dir_dictionary as dird

def perform_registrations():
    """Overall script to perform both mmp and shg registrations
    
    Produces images at each step 
    
    01 - Resized images 
    02 - Registered images
    03 - Registered images maskped to MMP boundaries"""
    
    dir_dict = dird.create_dictionary()
      
    resize_images(dir_dict)

    register_small_images(dir_dict)
    mask_small_images(dir_dict)

    apply_transform_to_large_images(dir_dict)
    mask_large_images(dir_dict)
    
    



def resize_images(dir_dict):
    """Resize the small MMP to ~ PS resolution.
        Resize the large PS images to ~ small MMP resolution
        Resize the large SHG images to ~ small MMP resolution"""
        
    trans.bulk_resize_image(dir_dict["mmp_small"],
                           dir_dict["ps_large"],dir_dict["ps_small"],
                           'PS_Small')
    
    trans.bulk_resize_image(dir_dict["mmp_small"],
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
    """Set all pixels outside the MMP ROI as 0 for PS and SHG"""
    proc.bulk_apply_mask(dir_dict["ps_small"], dir_dict['mmp_small_reg'],
                         dir_dict["ps_small_mask"], 'PS_Small_Masked')
    
    proc.bulk_apply_mask(dir_dict["shg_small_reg"], dir_dict['mmp_small_reg'],
                         dir_dict["shg_small_mask"], 'SHG_Small_Masked')

    return


def apply_transform_to_large_images(dir_dict):
    trans.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["mmp_large"],
                              dir_dict["mmp_large_reg"],
                              dir_dict["mmp_small_reg"],
                              'MMP_Large_Reg')
    
    trans.bulk_apply_transform(dir_dict["ps_large"],
                              dir_dict["shg_large"],
                              dir_dict["shg_large_reg"],
                              dir_dict["shg_small_reg"], 
                              'SHG_Large_Reg')


def mask_large_images(dir_dict):
    """Set all pixels outside the MMP ROI as 0 for PS and SHG"""
    proc.bulk_apply_mask(dir_dict["ps_large"], dir_dict['mmp_large_reg'],
                         dir_dict["ps_large_mask"], 'PS_Large_Masked')
    
    proc.bulk_apply_mask(dir_dict["shg_large_reg"], dir_dict['mmp_large_reg'],
                         dir_dict["shg_large_mask"], 'SHG_Large_Masked')
    
    return



perform_registrations()

    
