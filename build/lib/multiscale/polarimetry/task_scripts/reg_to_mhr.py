import multiscale.itk.registration as reg
import multiscale.polarimetry.task_scripts.dir_dictionary as dird

# path_large_reg = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Registered images\RegToMHR\SHG_Large_Reg')
# path_small_reg = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Registered images\RegToMHR\SHG_Small_Reg')

skip_existing_images = True

dir_dict = dird.create_dictionary()

# reg.bulk_supervised_register_images(
#     dir_dict["mhr_small"],
#     dir_dict["shg_small"],
#     path_small_reg, 'SHG_Small_Reg',
#     skip_existing_images=skip_existing_images, iterations=3)
#
# trans.bulk_apply_transform(dir_dict["mhr_large"],
#                            dir_dict["shg_large"],
#                            path_small_reg,
#                            path_large_reg, 'SHG_Large_Reg',
#                            skip_existing_images=skip_existing_images)

parameters = reg.setup_registration_parameters()

reg.bulk_supervised_register_images(
    dir_dict["shg_large"],
    dir_dict["mhr_large"],
    dir_dict["mhr_large_reg"], 'MHR_Large_Reg',
    skip_existing_images=True, registration_parameters=parameters)