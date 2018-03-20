# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""


import os
import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itkscripts as mitk


def create_dir_dictionary():
    base_dir = os.path.normpath('F:\Box Sync\Research\Polarimetry')
    
                                
    
    return dir_dict

def perform_registrations(base_dir = os.path.normpath('F:\Box Sync\Research\Polarimetry'),
                          prep_dir = '02 - Python prepped images',
                          resize_dir = '01 - Resizing images',
                          reg_crop_dir = '02 - Registered and cropped images'):
    """Overall script to perform both mmp and shg registrations, along with mask"""
    
    
    ps_dir = os.path.join(base_dir, prep_dir, 'PS_BasicCorrected')
    mmp_dir = os.path.join(base_dir, prep_dir, 'MMP')
    shg_dir = os.path.join(base_dir, prep_dir, 'SHG')
    
    
    #Resize images
    ps_dir_small = os.path.join(base_dir,resize_dir,'PS_Small')
    shg_dir_small = os.path.join(base_dir,resize_dir,'SHG_Small')
    mmp_dir_large = os.path.join(base_dir,resize_dir,'MMP_Large')
    
    mitk.bulk_resize_image(mmp_dir,ps_dir,ps_dir_small,'PS_Small')
    mitk.bulk_resize_image(ps_dir_small,shg_dir,shg_dir_small,'SHG_Small')
    mitk.bulk_resize_image(ps_dir,mmp_dir,mmp_dir_large,'MMP_Large')
    
    
    #Register small images
    mmp_dir_small_registered = os.path.join(base_dir,reg_crop_dir,'MMP_Small_Registered')
    shg_dir_small_registered = os.path.join(base_dir,reg_crop_dir,'SHG_Small_Registered')

    mitk.bulk_supervised_register_images(ps_dir_small,mmp_dir,mmp_dir_small_registered, 'MMP_Small_Registered')
    mitk.bulk_supervised_register_images(ps_dir_small,shg_dir_small,shg_dir_small_registered,'SHG_Small_Registered')


    #Crop small images
    ps_dir_small_cropped = os.path.join(base_dir,reg_crop_dir,'PS_Small_Cropped')
    mmp_dir_small_registered_cropped = os.path.join(os.path.join(base_dir,reg_crop_dir,'MMP_Small_Registered_Cropped'))
    shg_dir_small_registered_cropped = os.path.join(base_dir,reg_crop_dir,'SHG_Small_Registered_Cropped')

        


    #Register large images
    mmp_dir_large_registered = os.path.join(base_dir,reg_crop_dir,'MMP_Large_Registered')
    shg_dir_large_registered = os.path.join(base_dir,reg_crop_dir,'SHG_Large_Registered_Cropped')
    
    mitk.bulk_apply_transform(ps_dir,mmp_dir_large,mmp_dir_small_registered,mmp_dir_large_registered,'MMP_Large_Registered')
    mitk.bulk_apply_transform(ps_dir,shg_dir,shg_dir_small_registered, shg_dir_large_registereed, 'SHG_Large_Registered')



    #Crop large images
    ps_dir_large_cropped = os.path.join(base_dir,reg_crop_dir,'PS_Large_Cropped')
    mmp_dir_large_registered_cropped = os.path.join(base_dir,reg_crop_dir,'MMP_Large_Registered_Cropped')
    shg_dir_large_registered_cropped = os.path.join(base_dir,reg_crop_dir,'SHG_Large_Registered_Cropped')


def resize_images(base_dir, prep_dir, resize_dir)
    
def register_small_to_large(mmp_dir, ps_dir, crop = None):
    """Register MMP images to PS images.
    
    Output: A transform file
            Small registered MMP images
            Large registered MMP images
            cropped PS images
        """
    return

def register_large_to_small(shg_dir,ps_dir):
    """Register SHG images to PS images.
    
    Output: A transform file
        
            Small registered and cropped SHG images
            Large registered and cropped SHG images
        """
    return

def compare_ssim(dirOne, dirTwo):
    """Compare SSIM between two file directories
    """
    return

def downsample_ps_and_shg():
    return


    
