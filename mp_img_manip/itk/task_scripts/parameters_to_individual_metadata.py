"""
This script converts from the deprecated method of writing a single image parameters file holder both initial
transform and image properties such as spacing, to individual files holding the metadata and the initial transform.

The metadata is a custom txt file but the initial transform is native SITK
"""

import SimpleITK as sitk
from pathlib import Path
import pandas as pd

def parameters_file_to_metadata(dir_params):
        path_params = Path(dir_params, 'Image Parameters.csv')