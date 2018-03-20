# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import os
import mp_img_manip.itkscripts as mitk



def perform_registrations():
    """Overall script to perform both mmp and shg registrations, along with mask"""
    
    dir_dict = create_dir_dictionary()
      
    resize_images(dir_dict)

    register_small_images(dir_dict)
    crop_small_images(dir_dict)

    apply_transform_to_large_images(dir_dict)
    crop_large_images(dir_dict)
    
    

def create_dir_dictionary(base_dir = os.path.normpath('F:\Box Sync\Research\Polarimetry'),
                          prep_dir = '02 - Python prepped images',
                          resize_dir = '03 - Mid-python analysis images\\01 - Resizing images',
                          reg_crop_dir = '03 - Mid-python analysis images\\02 - Registered and cropped images'):
    dir_dict = {
    "ps_dir_large" : os.path.join(base_dir, prep_dir, 'PS_BasicCorrected'),
    "mmp_dir_small" : os.path.join(base_dir, prep_dir, 'MMP'),
    "shg_dir_large" : os.path.join(base_dir, prep_dir, 'SHG'),
    
    "ps_dir_small" : os.path.join(base_dir,resize_dir,'PS_Small'),
    "shg_dir_small" : os.path.join(base_dir,resize_dir,'SHG_Small'),
    "mmp_dir_large" : os.path.join(base_dir,resize_dir,'MMP_Large'),
                                
    "mmp_dir_small_registered" : os.path.join(base_dir,reg_crop_dir,'MMP_Small_Registered'),
    "shg_dir_small_registered" : os.path.join(base_dir,reg_crop_dir,'SHG_Small_Registered'),

    "mmp_dir_large_registered" : os.path.join(base_dir,reg_crop_dir,'MMP_Large_Registered'),
    "shg_dir_large_registered" : os.path.join(base_dir,reg_crop_dir,'SHG_Large_Registered_Cropped'),

    "ps_dir_small_cropped" : os.path.join(base_dir,reg_crop_dir,'PS_Small_Cropped'),
    "mmp_dir_small_registered_cropped" : os.path.join(os.path.join(base_dir,reg_crop_dir,'MMP_Small_Registered_Cropped')),
    "shg_dir_small_registered_cropped" : os.path.join(base_dir,reg_crop_dir,'SHG_Small_Registered_Cropped'),

    "ps_dir_large_cropped" : os.path.join(base_dir,reg_crop_dir,'PS_Large_Cropped'),
    "mmp_dir_large_registered_cropped" : os.path.join(base_dir,reg_crop_dir,'MMP_Large_Registered_Cropped'),
    "shg_dir_large_registered_cropped" : os.path.join(base_dir,reg_crop_dir,'SHG_Large_Registered_Cropped')}

    return dir_dict    


def resize_images(dir_dict):
    """Resize the small MMP images to be of similar resolution to the large PS images.
        Resize the large PS images to be of similar resolution to the small MMP images
        Resize the large SHG images to be of similar resolution to the small MMP images"""
        
    mitk.bulk_resize_image(dir_dict["mmp_dir_small"],
                           dir_dict["ps_dir_large"],dir_dict["ps_dir_small"],
                           'PS_Small')
    
    mitk.bulk_resize_image(dir_dict["ps_dir_small"],
                           dir_dict["shg_dir_large"],dir_dict["shg_dir_small"],
                           'SHG_Small')
    
    mitk.bulk_resize_image(dir_dict["ps_dir_large"],
                           dir_dict["mmp_dir_small"],dir_dict["mmp_dir_large"],
                           'MMP_Large')    



def register_small_images(dir_dict):
    """Register the small MMP to small PS.  Small SHG to small PS"""
    mitk.bulk_supervised_register_images(dir_dict["ps_dir_small"],
                                         dir_dict["mmp_dir_small"], dir_dict["mmp_dir_small_registered"],
                                         'MMP_Small_Registered')
    
    mitk.bulk_supervised_register_images(dir_dict["ps_dir_small"],
                                         dir_dict["shg_dir_small"],dir_dict["shg_dir_small_registered"],
                                         'SHG_Small_Registered')


def crop_small_images(dir_dict):
    return


def apply_transform_to_large_images(dir_dict):
    mitk.bulk_apply_transform(dir_dict["ps_dir_large"],
                              dir_dict["mmp_dir_large"], dir_dict["mmp_dir_large_registered"],
                              dir_dict["mmp_dir_small_registered"],
                              'MMP_Large_Registered')
    
    mitk.bulk_apply_transform(dir_dict["ps_dir_large"],
                              dir_dict["shg_dir_large"], dir_dict["shg_dir_large_registered"],
                              dir_dict["shg_dir_small_registered"], 
                              'SHG_Large_Registered')


def crop_large_images(dir_dict):
    return




    
