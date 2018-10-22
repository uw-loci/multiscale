"""
This script converts from the deprecated method of writing a single image parameters file holder both initial
transform and image properties such as spacing, to individual files holding the metadata and the initial transform.

The metadata is a custom txt file but the initial transform is native SITK
"""

import SimpleITK as sitk
from pathlib import Path
import pandas as pd
import multiscale.itk.metadata as meta


def parameters_file_to_metadata(dir_params):
        path_params = Path(dir_params, 'Image Parameters.csv')
        df_params = pd.read_csv(path_params, index_col=0)
        
        for idx in df_params.index:
                image_parameters = df_params.loc[idx]
                path_image= Path(dir_params, idx)
                path_metadata = Path(dir_params, Path(idx).stem + '_metadata.txt')
                
                if path_metadata.is_file():
                        return
                else:
                        image = sitk.ReadImage(str(path_image))
                        print('Adjusting {0}'.format(idx))
                        unit = 'microns'
                        
                        spacing = [float(image_parameters['Spacing']),
                                   float(image_parameters['Spacing'])]
                        image.SetSpacing(spacing)
                        image.SetMetaData('Unit', unit)
                        
                        meta.write_image(image, path_image)
        
                
dir_params = r'F:\Research\Polarimetry\Data 02 - Python prepped images\SHG_Large'

parameters_file_to_metadata(dir_params)