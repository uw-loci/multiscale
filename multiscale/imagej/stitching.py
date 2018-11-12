"""
A module for image stitching using the ImageJ interface.

Copyright (c) 2018, Michael Pinkert
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Laboratory for Optical and Computational Instrumentation nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
from pathlib import Path
import tempfile
import os
import SimpleITK as sitk
import multiscale.imagej.bigdata as big


class BigStitcher(object):
        """
        Image stitching using the BigStitcher ImageJ plugin
        """
        def __init__(self, ij):
                """Class for using the BigStitcher plugin on a python interface"""
                self._ij = ij

        def stitch_from_files(self, dataset_args: dict, fuse_args: dict):
                # Stitch
                self._define_dataset(dataset_args)
                self._fuse_dataset(fuse_args)

        def stitch_from_numpy(self, images_np: np.ndarray, dataset_args: dict, fuse_args: dict):
                with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                                temp_dir_str = str(temp_dir).replace('\\', '/')
                                dataset_args['path'] = str(temp_dir_str)
                                self._save_numpy_images(temp_dir, images_np)
                                self.stitch_from_files(dataset_args, fuse_args)
                        except:
                                raise ImportError('ImageJ not configured correctly')

        def _save_numpy_images(self, save_dir, numpy_images: np.ndarray):
                """
                Save a numpy array into 32bit float tif files by iterating along the first axis.
                :param save_dir: Directory to save the images in
                :param numpy_images: Array of images to save
                :return:
                """
                # todo: save images in imagej.py
                print('Saving images into tif files')
                for idx in range(len(numpy_images)):
                        save_path = Path(save_dir, 'Image_{}.tif'.format(idx))
                        img = sitk.GetImageFromArray(numpy_images[idx])
                        cast = sitk.Cast(img, sitk.sitkFloat32)
                        sitk.WriteImage(cast, str(save_path))

        def _define_dataset(self, dataset_args):
                """
                Use the BigStitcher Define dataset macro to make an HDF5 dataset for the given files
                :param dataset_args: Custom arguments for the fusion
                :return:
                """
                function_call = "Define dataset ..."
                #macro = 'run(\"Define dataset ...\")'
                print('Defining dataset from {}'.format(dataset_args['path']))

                #dataset_args = self._ij.py.to_java(self._populate_dataset_args(dataset_args))
                dataset_args = self._populate_dataset_args(dataset_args)
                macro = big.assemble_run_statement(function_call, dataset_args)
                
                self._ij.py.run_macro(macro)

        def _fuse_dataset(self, fuse_args):
                return

        def _populate_dataset_args(self, dataset_args):
                """
                Populate a set of define dataset arguments with default values

                :param dataset_args: User given values for some of the arguments
                :return:
                """

                args = {
                        'define_dataset': '[Automatic Loader (Bioformats based)]',
                        'project_filename': 'dataset.xml',
                        'path': '../StitchedImages',
                        'exclude': '10',
                        'pattern_0': 'Tiles',
                        'modify_voxel_size?': '',
                        'voxel_size_x': '1',
                        'voxel_size_y': '1',
                        'voxel_size_z': '1',
                        'voxel_size_unit': 'mm',
                        'move_tiles_to_grid_(per_angle)?': '[Move Tile to Grid (Macro-scriptable)]',
                        'grid_type': '[Right & Down             ]',
                        'tiles_x': 1,
                        'tiles_y': 1,
                        'tiles_z': 1,
                        'overlap_x_(%)': '10',
                        'overlap_y_(%)': '10',
                        'overlap_z_(%)': '10',
                        'keep_metadata_rotation': '',
                        'how_to_load_images': '[Re-save as multiresolution HDF5]',
                        'dataset_save_path': '../StitchedImages/',
                        'subsampling_factors': '[{ {1,1,1}, {2,2,2}, {4,4,4} }]',
                        'hdf5_chunk_sizes': '[{ {16,16,16}, {16,16,16}, {16,16,16} }]',
                        'timepoints_per_partition': '1',
                        'setups_per_partition': '0',
                        'use_deflate_compression': '',
                        'export_path': '../StitchedImages/dataset'
                }

                for key in dataset_args:
                        args[key] = dataset_args[key]

                return args

        def _populate_stitching_args(self):
                return

        def _populate_fuse_args(self, fuse_args):
                return

# macro = """run("BigStitcher", "select=define define_dataset=[Automatic Loader (Bioformats based)] """ + \
# """project_filename=dataset.xml path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt """ + \
# """exclude=10 pattern_0=Tiles modify_voxel_size? voxel_size_x=25.7359 voxel_size_y=25.7359 """ +\
# """voxel_size_z=50 voxel_size_unit=µm move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)] """+\
# """grid_type=[Right & Down             ] tiles_x=3 tiles_y=1 tiles_z=1 """ +\
# """overlap_x_(%)=34 overlap_y_(%)=10 overlap_z_(%)=10 keep_metadata_rotation """+\
# """how_to_load_images=[Re-save as multiresolution HDF5] """ +\
# """dataset_save_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt """ +\
# """subsampling_factors=[{ {1,1,1}, {2,2,2} }] hdf5_chunk_sizes=[{ {16,16,16}, {16,16,16} }] """+\
# """timepoints_per_partition=1 setups_per_partition=0 use_deflate_compression """+\
# """export_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt/dataset");
# """


"""
example pairwise shift


run("Calculate pairwise shifts ...", "select=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt/dataset.xml
process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations]
process_tile=[All tiles] process_timepoint=[All Timepoints] method=[Phase Correlation] downsample_in_x=2
downsample_in_y=2 downsample_in_z=2");

"""

"""
example image fusion

run("Fuse dataset ...", "select=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt//dataset_resaved.xml
process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations]
process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[Currently Selected Views]
downsampling=1 pixel_type=[32-bit floating point] interpolation=[Linear Interpolation] image=[Precompute Image]
blend produce=[Each timepoint & channel] fused_image=[Save as new XML Project (TIFF)]
select=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt//tiff_fused.xml");
"""

"""

run("Define dataset ...", "define_dataset=[Automatic Loader (Bioformats based)] project_filename=dataset.xml
path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt
exclude=10 pattern_0=Tiles modify_voxel_size? voxel_size_x=25.7359 voxel_size_y=25.7359 voxel_size_z=50
voxel_size_unit=µm move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)]
grid_type=[Right & Down             ] tiles_x=3 tiles_y=1 tiles_z=1
overlap_x_(%)=34 overlap_y_(%)=10 overlap_z_(%)=10 keep_metadata_rotation
how_to_load_images=[Re-save as multiresolution HDF5]
dataset_save_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt
subsampling_factors=[{ {1,1,1}, {2,2,2}, {4,4,4} }]
hdf5_chunk_sizes=[{ {16,16,16}, {16,16,16}, {16,16,16} }]
timepoints_per_partition=1 setups_per_partition=0
use_deflate_compression export_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt/dataset");
"""

"""
run("Define dataset ...",
 "path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt
  pattern_0=Tiles modify_voxel_size? voxel_size_x=25.7359 voxel_size_y=25.7359 voxel_size_z=50 voxel_size_unit=µm
   move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)]
    grid_type=[Right & Down             ]
    tiles_x=3 tiles_y=1 tiles_z=1 overlap_x_(%)=34 overlap_y_(%)=10 overlap_z_(%)=10
    keep_metadata_rotation
    how_to_load_images=[Re-save as multiresolution HDF5]
    dataset_save_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt
    timepoints_per_partition=1 setups_per_partition=0
 use_deflate_compression export_path=F:/Research/LINK/US/ProngPhantom-BrokenProng_11Volt/dataset");

"""



