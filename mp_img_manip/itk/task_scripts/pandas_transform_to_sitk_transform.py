"""
The previous versions of the code used a custom function to save transforms as pandas csvs.  This method is more
complicated and prone to error than SimpleITKs native method, as I need to specify a version for each possible
transform.

This script is meant to convert transforms made using the old pandas method into the native SimpleITK method.
"""

import SimpleITK as sitk
from pathlib import Path
import os

import mp_img_manip.bulk_img_processing as blk
import mp_img_manip.itk.metadata as meta
import mp_img_manip.itk.transform as trans
import mp_img_manip.itk.itk_plotting as itkplot

fix_path = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 02 - Resizing images\SHG_Small',
                '1045-M1_SHG_Small.tif')
mov_path = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 02 - Resizing images\MHR_Small',
                '1045-M1_MHR_Small.tif')

reference_path = Path(r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Registered images\Old registrations\MHR_Small_Reg',
                      '1045-M1_MHR_Small_Reg.tif')

fix_img = meta.setup_image(fix_path, change_origin=False)
mov_img = meta.setup_image(mov_path)

reg_old = trans.apply_transform_pandas(fix_img, mov_img, reference_path)


transform_path = os.path.join(reference_path.parent, 'Transforms.csv')
transform_params = blk.read_pandas_row(transform_path, reference_path.name, 'Image')
transform = sitk.AffineTransform(2)

transform.Rotate(0, 1, transform_params['Rotation'], pre=True)

matrix = [transform_params['Matrix Top Left'],
          transform_params['Matrix Top Right'],
          transform_params['Matrix Bottom Left'],
          transform_params['Matrix Bottom Right']]

transform.SetMatrix(matrix)
transform.SetTranslation([transform_params['X Translation'] - transform_params['X Origin'],
                          transform_params['Y Translation'] - transform_params['Y Origin']])

mov_img.SetOrigin([0, 0])

itkplot.plot_overlay(reg_old, mov_img, transform)
