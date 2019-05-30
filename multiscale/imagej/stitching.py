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
import tiffile as tif
import os

import multiscale.utility_functions as util


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
                # todo: rename fused file and/or open in imagej and save as custom tif (8 bit?)

        def stitch_from_numpy(self, images_np: np.ndarray, dataset_args: dict, fuse_args: dict,
                              intermediate_save_dir=None, output_name='fused_tp_0_ch_0.tif'):
                """
                Stitch images from a 4d numpy array
                :param images_np: The array of numpy images
                :param dataset_args: Arguments for the stitching
                :param fuse_args: Arguments for image fusion
                :param intermediate_save_dir: Where to save the intermediate .tif files
                :return:
                """
                # todo: Have it save the set/save spacing correctly as well
                output_path = Path(fuse_args['output_file_directory'].replace('[', '').replace(']', ''),
                                   output_name)
                if output_path.is_file():
                        if not util.query_yes_no(
                                    '{} already exists.  Overwrite previous result? >> '.format(output_path)):
                                return

                if intermediate_save_dir is None:
                        with tempfile.TemporaryDirectory() as temp_dir:
                                self._dataset_from_numpy(images_np, dataset_args, fuse_args, temp_dir)
                else:
                        self._dataset_from_numpy(images_np, dataset_args, fuse_args, intermediate_save_dir)
                        
                if output_name != 'fused_tp_0_ch_0.tif':
                        original_path = Path(fuse_args['output_file_directory'], 'fused_tp_0_ch_0.tif')
                        output_path = Path(fuse_args['output_file_directory'], output_name)
                        print('Renaming {0} to {1}'.format(original_path.name, output_path.name))
                        try:
                                os.rename(original_path, output_path)
                        except WindowsError:
                                os.remove(output_path)
                                os.rename(original_path, output_path)
                        

        def _dataset_from_numpy(self, images_np, dataset_args, fuse_args, intermediate_save_dir):
                """Helper for stitch from numpy"""
                dataset_args['path'] = intermediate_save_dir
                self._save_numpy_images(intermediate_save_dir, images_np, dataset_args)
                self.stitch_from_files(dataset_args, fuse_args)

        def _save_numpy_images(self, save_dir, numpy_images: np.ndarray, dataset_args):
                """
                Save a numpy array into 32bit float tif files by iterating along the first axis.
                :param save_dir: Directory to save the images in
                :param numpy_images: Array of images to save
                :return:
                """
                print('Saving images into tif files')
                for idx in range(len(numpy_images)):
                        save_path = Path(save_dir, 'Image_{}.tif'.format(idx))
                        if save_path.exists():
                                print('{} already exists, skipping save image.'.format(save_path.name))
                                continue
                                
                        # Change shape to TZCYXS order
                        ijstyle = numpy_images[idx]
                        shape = ijstyle.shape
                        if len(shape) == 3:
                                ijstyle.shape = 1, shape[0], 1, shape[1], shape[2], 1
                        elif len(shape) == 2:
                                ijstyle.shape = 1, 1, 1, shape[0], shape[1], 1
                        else:
                                raise NotImplementedError('Saving has not been implemented for this image type.'
                                                          '  2D and 3 D images only')
                        
                        tif.imwrite(save_path, ijstyle, imagej=True,
                                    resolution=(1. / dataset_args['voxel_size_x'], 1. / dataset_args['voxel_size_y']),
                                    metadata={'spacing': dataset_args['voxel_size_z'], 'unit': 'um'})

        def _define_dataset(self, dataset_args):
                """
                Use the BigStitcher Define dataset macro to make an HDF5 dataset for the given files
                :param dataset_args: Custom arguments for the fusion
                :return:
                """
                plugin = "Define dataset ..."
                dataset_path = Path(dataset_args['dataset_save_path'], dataset_args['project_filename'])
                if dataset_path.is_file():
                        print('{} already exists, skipping save dataset.'.format(dataset_path))
                else:
                        print('Defining dataset from {}'.format(dataset_args['path']))
                        dataset_args = self._populate_dataset_args(dataset_args)
                        self._ij.py.run_plugin(plugin, args=dataset_args)

        def _fuse_dataset(self, fuse_args):
                plugin = "Fuse dataset ..."
                print('Fusing dataset from {}'.format(Path(fuse_args['select'])))
                fuse_args = self._populate_fuse_args(fuse_args)
                self._ij.py.run_plugin(plugin, args=fuse_args)
                
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
                        'modify_voxel_size?': None,
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
                        'keep_metadata_rotation': None,
                        'how_to_load_images': '[Re-save as multiresolution HDF5]',
                        'dataset_save_path': None,
                        'subsampling_factors': '[{ {1,1,1}, {2,2,2}, {4,4,4} }]',
                        'hdf5_chunk_sizes': '[{ {16,16,16}, {16,16,16}, {16,16,16} }]',
                        'timepoints_per_partition': '1',
                        'setups_per_partition': '0',
                        'use_deflate_compression': None,
                        'export_path': None
                }

                for key in dataset_args:
                        args[key] = dataset_args[key]

                return args

        def _populate_stitching_args(self):
                return

        def _populate_fuse_args(self, fuse_args):
                """
                Populate a set of fuse dataset arguments, filling in any missing values
                
                :param fuse_args: Dictionary containing non-default arguments
                :return:
                """
                args = {
                        'select': None,
                        'process_angle': '[All angles]',
                        'process_channel': '[All channels]',
                        'process_illumination': '[All illuminations]',
                        'process_tile': '[All tiles]',
                        'process_timepoint': '[All Timepoints]',
                        'bounding_box': '[Currently Selected Views]',
                        'downsampling': '1',
                        'pixel_type': '[32-bit floating point]',
                        'interpolation': '[Linear Interpolation]',
                        'image': 'Virtual',
                        'blend': None,
                        'preserve_original': False,
                        'produce': '[Each timepoint & channel]',
                        'fused_image': '[Save as (compressed) TIFF stacks]',
                        'output_file_directory': None
                }
                
                for key in fuse_args:
                        args[key] = fuse_args[key]
                        
                return args

