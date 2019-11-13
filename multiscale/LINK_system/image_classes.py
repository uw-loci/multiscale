import numpy as np
import multiscale.utility_functions as util
import tiffile as tif
from pathlib import Path
import multiscale.ultrasound.reconstruction as recon


def convert_oct_to_tif(mat_path: Path, output_folder, resolution, overwrite=False):
        """
        Convert a .mat OCT image file from LINK to
        :param mat_path:
        :param output_folder:
        :param resolution: numpy array of [x, y, z] resolution
        :param overwrite: Boolean.  True if you wish to overwrite pre-existing files, false if not
        :return:
        """

        output_path = Path(output_folder, mat_path.stem + '.tif')
        
        if output_path.is_file() and not overwrite:
                print('File already exists.  Skipping writing.')
                return
        
        oct_array = util.load_mat(mat_path, 'ropd_vol')
        bmode_array = recon.iq_to_db(oct_array)
        
        zyx_array = np.transpose(bmode_array, (2, 0, 1))
        
        
        ijstyle = zyx_array.astype(np.float32)
        shape = ijstyle.shape
        ijstyle.shape = 1, shape[0], 1, shape[1], shape[2], 1
        
        tif.imwrite(output_path, ijstyle, imagej=True,
                    resolution=(1./resolution[0], 1./resolution[1]),
                    metadata={'spacing': resolution[2], 'unit': 'um'})


