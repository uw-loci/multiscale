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
registration_parameters = reg.setup_registration_parameters(scale=1, iterations=100, learning_rate=np.double(3), min_step=np.double(0.01),
                                  gradient_tolerance=np.double(1E-6), sampling_percentage=0.01)

#Modify these paths to go to the appropriate directories/images
czi_images_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR czi images')
img_to_register_path = Path(czi_images_dir, '1367 slide 5.czi')
img_output_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR Registered')
transform_output_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\LR Transforms')
transform_prefix = 'MLR_Position'

#Change this to whatever resolution the images are
img_resolution = 2.016

#Run the commands
calculate_polarization_state_transforms(img_to_register_path, img_resolution, transform_output_dir, transform_prefix,
                                        registration_parameters)
bulk_apply_polarization_transforms(czi_images_dir, img_output_dir, transform_output_dir, transform_prefix, img_resolution)


javabridge.kill_vm()
