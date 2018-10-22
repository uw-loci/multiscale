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

from multiscale.polarimetry.preprocessing import calculate_polarization_state_transforms, \
        bulk_apply_polarization_transforms

javabridge.start_vm(class_path=bf.JARS, max_heap_size='8G')

mhr_dir = Path(r'C:\Users\mpinkert\Box\Research\Polarimetry\Polarimetry - Raw Data\2018.06.14_80x')
mhr_path = Path(mhr_dir, 'WP2.czi')
output_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\MHR Registered')
transform_dir = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\MHR Transforms')
transform_prefix = 'MHR_Position'
mlr_resolution = 2.016
mhr_resolution = 0.81


calculate_polarization_state_transforms(mhr_path, mhr_resolution, transform_dir)
bulk_apply_polarization_transforms(mhr_dir, output_dir, transform_dir, transform_prefix, mhr_resolution)


javabridge.kill_vm()
