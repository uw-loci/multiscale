"""
The previous versions of the code used a custom function to save transforms as pandas csvs.  This method is more
complicated and prone to error than SimpleITKs native method, as I need to specify a version for each possible
transform.

This script is meant to convert transforms made using the old pandas method into the native SimpleITK method.
"""

import SimpleITK as sitk
from pathlib import Path
import pandas as pd


def pandas_csv_to_transforms(tform_dir, output_dir):
        csv_path = Path(tform_dir, 'Transforms.csv')
        df_tforms = pd.read_csv(csv_path, index_col='Image')
        
        for idx in df_tforms.index:
                transform_params = df_tforms.loc[idx]
                transform = sitk.AffineTransform(2)
                
                transform.Rotate(0, 1, transform_params['Rotation'], pre=True)
                
                matrix = [transform_params['Matrix Top Left'],
                          transform_params['Matrix Top Right'],
                          transform_params['Matrix Bottom Left'],
                          transform_params['Matrix Bottom Right']]
                
                transform.SetMatrix(matrix)
                transform.SetTranslation([transform_params['X Translation'] - transform_params['X Origin'],
                                          transform_params['Y Translation'] - transform_params['Y Origin']])
        
                img_path = Path(idx)
                file_parts = img_path.stem.split('_')
                tform_path = Path(output_dir, file_parts[0] +'_' + file_parts[1] + '_initial.tfm')
                
                sitk.WriteTransform(transform, str(tform_path))
        


tform_dir = r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Step 03 - Registered images\RegToMHR\SHG_Small_Reg'
output_dir = r'F:\Research\Polarimetry\Data 03 - Mid-python analysis images\Transforms\SHG to MHR'
pandas_csv_to_transforms(tform_dir, output_dir)