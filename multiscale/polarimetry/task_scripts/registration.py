# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""
import multiscale.itk.registration as reg
import multiscale.itk.transform as trans
import multiscale.itk.process as proc
import multiscale.polarimetry.dir_dictionary as dird


def perform_registrations(dir_dict: dict, skip_existing_images=True):
        """Overall script to perform both mmp and shg registrations
        
        Produces images at each step
        00 - Polscope intensity to retardance
        01 - Resized images
        02 - RegiMed images
        03 - RegiMed images thresholded to a value"""
        
        
        #    pol.bulk_intensity_to_retardance(dir_dict['ps_large'],
        #                                     dir_dict['ps_large_ret'],
        #                                     'PS_Large_Ret',
        #                                     skip_existing_images=skip_existing_images)

        reg.bulk_supervised_register_images(dir_dict["shg_large"],
                                            dir_dict["mhr_large"],
                                            dir_dict["mhr_large_reg"], 'MHR_Registered',
              
                                            skip_existing_images=skip_existing_images)
        
def apply_transforms(dir_dict: dict, skip_existing_images=True):
        trans.bulk_apply_transform(dir_dict['shg_large'],
                                   dir_dict['mhr_large_orient'],
                                   dir_dict['mhr_large_reg'],
                                   dir_dict['mhr_large_reg_orient'], 'MHR_Orient_Registered',
                                   skip_existing_images=skip_existing_images)
        
        
dir_dict = dird.create_dictionary()
perform_registrations(dir_dict)
apply_transforms(dir_dict)

