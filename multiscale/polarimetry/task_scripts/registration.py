# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:52:18 2018

@author: mpinkert
"""
import multiscale.itk.registration as reg
import multiscale.itk.transform as trans
import multiscale.itk.process as proc
import multiscale.polarimetry.dir_dictionary as dird


def perform_registrations(dir_dict: dict, registration_parameters=None, skip_existing_images=True):
        """Overall script to perform both mmp and shg registrations
        
        Produces images at each step
        00 - Polscope intensity to retardance
        01 - Resized images
        02 - RegiMed images
        03 - RegiMed images thresholded to a value"""
        
        
        #    retard.bulk_intensity_to_retardance(dir_dict['ps_large'],
        #                                     dir_dict['ps_large_ret'],
        #                                     'PS_Large_Ret',
        #                                     skip_existing_images=skip_existing_images)

        reg.bulk_supervised_register_images(dir_dict["shg_large"],
                                            dir_dict["mhr_large"],
                                            dir_dict["mhr_large_reg"], 'MHR_Registered',
                                            skip_existing_images=skip_existing_images,
                                            registration_parameters=registration_parameters)
        
        reg.bulk_supervised_register_images(dir_dict["shg_large"],
                                            dir_dict["mlr_large"],
                                            dir_dict["mlr_large_reg"], 'MLR_Registered',
                                            skip_existing_images=skip_existing_images,
                                            registration_parameters=registration_parameters)
        
        reg.bulk_supervised_register_images(dir_dict['shg_large'],
                                            dir_dict['ps'],
                                            dir_dict['ps_reg_raw'], 'PS_Registered',
                                            skip_existing_images=skip_existing_images,
                                            registration_parameters=registration_parameters)
        
def apply_transforms(dir_dict: dict, skip_existing_images=True):
        trans.bulk_apply_transform(dir_dict['shg_large'],
                                   dir_dict['mhr_large_orient'],
                                   dir_dict['mhr_large_reg'],
                                   dir_dict['mhr_large_reg_orient'], 'MHR_Orient_Registered',
                                   skip_existing_images=skip_existing_images)
        
        trans.bulk_apply_transform(dir_dict['shg_large'],
                                   dir_dict['mlr_large_orient'],
                                   dir_dict['mlr_large_reg'],
                                   dir_dict['mlr_large_reg_orient'], 'MLR_Orient_Registered',
                                   skip_existing_images=skip_existing_images)
        
        trans.bulk_apply_transform(dir_dict['shg_large'],
                                   dir_dict['ps_orient'],
                                   dir_dict['ps_reg'],
                                   dir_dict['ps_reg_orient_raw'], 'PS_Orient_Registered',
                                   skip_existing_images=skip_existing_images)
        
dir_dict = dird.create_dictionary()
perform_registrations(dir_dict)
apply_transforms(dir_dict)


# import multiscale.itk.registration as reg
# import multiscale.itk.transform as trans
# import multiscale.itk.process as proc
# import multiscale.polarimetry.dir_dictionary as dird
# from pathlib import Path
# moving_dir = Path(r'F:\Research\Polarimetry\Data 02 - Python prepped images\PS_Large')
# orient_dir = Path(r'F:\Research\Polarimetry\Data 02 - Python prepped images\PS_Large_Orient')
#
# fixed_dir = Path(r'F:\Research\Polarimetry\Data 02 - Python prepped images\SHG_Large')
# output_dir = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Registered images\PS_Large_Reg\Raw')
# orient_output_dir = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Registered images\PS_Large_Reg_Orient\Raw')
#
# pars = reg.setup_registration_parameters(scale=3)
#
# reg.bulk_supervised_register_images(fixed_dir, moving_dir, output_dir, 'PS_Reg', registration_parameters=pars)
# trans.bulk_apply_transform(fixed_dir, orient_dir, output_dir, orient_output_dir, "PS_Large_Registered_Orient")