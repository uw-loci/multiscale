"""
Mueller matrix polarimetry takes many different images of the same
sample using different input and output polarizations.  Changing the
output polarization on the instrument we are using changes the
optical path, and thus shifts the images.

This script is intended to register the images onto each other and
find a universal transform so that it can be applied to all future
images from the same source.  This will let us get better results with
the final Mueller image.
"""

import javabridge
import bioformats as bf
from pathlib import Path
import numpy as np

from multiscale.polarimetry.preprocessing import calculate_polarization_state_transforms
from multiscale.polarimetry.preprocessing import bulk_apply_polarization_transforms
import multiscale.itk.registration as reg


# Start the javabridge to enable bioformats
javabridge.start_vm(class_path=bf.JARS, max_heap_size='8G')

#Registration paramaters.  Adjust these to adjust how the registration performs
reg.setup_registration_parameters(scale=1, iterations=100, learning_rate=np.double(3), min_step=np.double(0.01),
                                  gradient_tolerance=np.double(1E-6), sampling_percentage=0.01)


# #MHR registration
# mhr_dir = Path(r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_80x')
# mhr_path = Path(mhr_dir, 'WP2.czi')
# mhr_output_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\HR Registered')
# mhr_transform_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\HR Transforms')
# mhr_transform_prefix = 'MHR_Position'
# mhr_resolution = 0.81
#
# calculate_polarization_state_transforms(mhr_path, mhr_resolution, mhr_transform_dir, mhr_transform_prefix,
#                                         scale=scale, iterations=iterations, learning_rate=learning_rate,
#                                         min_step=min_step,  gradient_tolerance=gradient_tolerance,
#                                         metric_sampling_percentage=metric_sampling_percentage)
# bulk_apply_polarization_transforms(mhr_dir, mhr_output_dir, mhr_transform_dir, mhr_transform_prefix, mhr_resolution,
#                                    registration_parameters)


#MLR registration
mlr_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR czi images')
mlr_path = Path(mlr_dir, '1367 slide 5.czi')
mlr_output_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR Registered')
mlr_transform_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR Transforms')
mlr_transform_prefix = 'MLR_Position'
mlr_resolution = 2.016

calculate_polarization_state_transforms(mlr_path, mlr_resolution, mlr_transform_dir, mlr_transform_prefix,
                                        registration_parameters)

bulk_apply_polarization_transforms(mlr_dir, mlr_output_dir, mlr_transform_dir, mlr_transform_prefix, mlr_resolution)


javabridge.kill_vm()
