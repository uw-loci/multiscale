# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""
import matplotlib as mpl
mpl.use('qt5agg')
import matplotlib.pyplot as plt
plt.ion()

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
    02 - RegiMed images
    03 - RegiMed images thresholded to a value"""
    
    dir_dict = dird.create_dictionary()

#    pol.bulk_intensity_to_retardance(dir_dict['ps_large'], 
#                                     dir_dict['ps_large_ret'],
#                                     'PS_Large_Ret',
#                                     skip_existing_images=skip_existing_images)

    mask_images(dir_dict, skip_existing_images=skip_existing_images)

    resize_images(dir_dict, skip_existing_images=skip_existing_images)

    register_small_images(dir_dict, skip_existing_images)
    apply_transform_to_large_images(dir_dict, skip_existing_images=skip_existing_images)

#    make_eightbit_images(dir_dict)
    

def resize_images(dir_dict, target_spacing=5, skip_existing_images=False):

#    trans.bulk_resize_to_target(
#            dir_dict["ps_large_ret"], dir_dict["ps_small"], 'PS_Small',
#            target_spacing,
#            skip_existing_images=skip_existing_images)
    
    trans.bulk_resize_to_target(
            dir_dict["shg_large"], dir_dict["shg_small"], 'SHG_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)
            
    trans.bulk_resize_to_target(
            dir_dict["mhr_large_mask"], dir_dict["mhr_small"], 'MHR_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)    
    
    trans.bulk_resize_to_target(
            dir_dict["mlr_large_mask"], dir_dict["mlr_small"], 'MLR_Small',
            target_spacing,
            skip_existing_images=skip_existing_images)    


def register_small_images(dir_dict, skip_existing_images=False):
    """Register the small MLR/MHR to SHG images, and PS to SHG"""
    reg.bulk_supervised_register_images(
            dir_dict["shg_small"],
            dir_dict["mlr_small"],
            dir_dict["mlr_small_reg"], 'MLR_Small_Reg',
            skip_existing_images=skip_existing_images)

    reg.bulk_supervised_register_images(
            dir_dict["shg_small"],
            dir_dict["mhr_small"],
            dir_dict["mhr_small_reg"], 'MHR_Small_Reg',
            skip_existing_images=skip_existing_images)

#    reg.bulk_supervised_register_images(
#            dir_dict["shg_small"],
#            dir_dict["ps_small"],
#            dir_dict["ps_small_reg"], 'PS_Small_Reg',
#            skip_existing_images=skip_existing_images)


def apply_transform_to_large_images(dir_dict, skip_existing_images=False):
    trans.bulk_apply_transform(dir_dict["shg_large"],
                              dir_dict["mlr_large_mask"],
                              dir_dict["mlr_small_reg"],
                              dir_dict["mlr_large_reg"], 'MLR_Large_Reg',
                              skip_existing_images=skip_existing_images)

    trans.bulk_apply_transform(dir_dict["shg_large"],
                              dir_dict["mhr_large_mask"],
                              dir_dict["mhr_small_reg"],
                              dir_dict["mhr_large_reg"], 'MHR_Large_Reg',
                              skip_existing_images=skip_existing_images)

#    trans.bulk_apply_transform(dir_dict["shg_large"],
#                              dir_dict["ps_large"],
#                              dir_dict["ps_small_reg"],
#                              dir_dict["ps_large_reg"], 'PS_Large_Reg',
#                              skip_existing_images=skip_existing_images)
    
    trans.bulk_apply_transform(dir_dict["shg_large"],
                               dir_dict["mlr_large_mask_orient"],
                               dir_dict["mlr_small_reg"],
                               dir_dict['mlr_large_reg_orient'],
                               'MLR_Large_Reg_orient',
                               skip_existing_images=skip_existing_images)

    trans.bulk_apply_transform(dir_dict["shg_large"],
                               dir_dict["mhr_large_mask_orient"],
                               dir_dict["mhr_small_reg"],
                               dir_dict['mhr_large_reg_orient'],
                               'MHR_Large_Reg_orient',
                               skip_existing_images=skip_existing_images)


def mask_images(dir_dict, skip_existing_images=False):
    """Set all pixels outside the MMP ROI as 0 for PS and SHG"""
    
    proc.bulk_threshold(
            dir_dict['mlr_large'], dir_dict['mlr_large_mask'],
            'MLR_Large_Mask',
            skip_existing_images=skip_existing_images)

    proc.bulk_apply_mask(
            dir_dict['mlr_large_orient'], dir_dict['mlr_large_mask'],
            dir_dict['mlr_large_mask_orient'],
            'MLR_Large_Mask_Orient',
            skip_existing_images=skip_existing_images)

    proc.bulk_threshold(
        dir_dict['mhr_large'], dir_dict['mhr_large_mask'],
        'MHR_Large_Mask',
        skip_existing_images=skip_existing_images)

    proc.bulk_apply_mask(
        dir_dict['mhr_large_orient'], dir_dict['mhr_large_mask'],
        dir_dict['mhr_large_mask_orient'],
        'MHR_Large_Mask_Orient',
        skip_existing_images=skip_existing_images)


#def make_eightbit_images(dir_dict):
##    proc.bulk_convert_to_eightbit(dir_dict["ps_large_mask"],
##                                  dir_dict['ps_large_8bit'],
##                                  'PS_Large_8Bit')
#    
#    proc.bulk_convert_to_eightbit(dir_dict["mhr_large_reg"],
#                                  dir_dict['mhr_large_8bit'],
#                                  'MHR_Large_8Bit')
#    
#    proc.bulk_convert_to_eightbit(dir_dict["mlr_large_reg"],
#                                  dir_dict['mlr_large_8bit'],
#                                  'MLR_Large_8Bit')
##
##    proc.bulk_convert_to_eightbit(dir_dict["ps_small_mask"],
##                                  dir_dict['ps_small_8bit'],
##                                  'PS_Small_8Bit')
##    
#    proc.bulk_convert_to_eightbit(dir_dict["mhr_small_reg"],
#                                  dir_dict['mhr_small_8bit'],
#                                  'MHR_Small_8Bit')
#    
#    proc.bulk_convert_to_eightbit(dir_dict["mlr_small_reg"],
#                                  dir_dict['mlr_small_8bit'],
#                                  'MLR_Small_8Bit')

dir_dict = dird.create_dictionary()
trans.bulk_resize_to_target(dir_dict["he_large"], dir_dict["he_small"], 'HE_Small',
                        5, skip_existing_images=True)
reg.bulk_supervised_register_images(dir_dict['shg_small'], dir_dict['he_small'], dir_dict['he_small_reg'], 'HE_Small_Reg')
#perform_registrations()

    
