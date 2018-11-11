"""Script for reconstructing ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import scipy.io as sio
from pathlib import Path
import numpy as np
import multiscale.utility_functions as util
import re
import SimpleITK as sitk
import multiscale.itk.metadata as meta
import multiscale.imagej.bigdata as bd
import h5py
import os
import tempfile


class UltrasoundImageAssembler(object):
        """
        todo: start generalizing this so it can work with multiple image types/kinds
        """
        def __init__(self, mat_dir: Path, output_dir: Path, pl_path: Path=None):
                self.mat_dir = mat_dir
                self.pl_path = pl_path
                self.output_dir = output_dir
                os.makedirs(output_dir, exist_ok=True)
                
                self.pos_list = []
                self.mat_list = []
                self.acq_params = {}
               
        def get_acquisition_parameters(self):
                """Get the US acquisition parameters"""
                return self.acq_params

        def _assemble_image(self, base_image_data='IQData'):
                self.pos_list = self._read_position_list()
                self.mat_list = self._read_sorted_list_mats()
                self._read_parameters(self.mat_list[0])
                
                image_list = self._mat_list_to_variable_list(base_image_data)
                separate_3d_images = self._image_list_to_laterally_separate_3d_images(image_list)
                
                self._stitch_images_from_temporary_directory(separate_3d_images)

        def _assemble_stitching_arguments_(self, provided_args):
                spacing = self._get_spacing()

                args = {
                        'define_dataset': '[Automatic Loader (Bioformats based)]',
                        'project_filename': 'dataset.xml',
                        'path': '../StitchedImages',
                        'exclude': '10',
                        'pattern_0': 'Tiles',
                        'modify_voxel_size?': None,
                        'voxel_size_x': spacing[0],
                        'voxel_size_y': spacing[1],
                        'voxel_size_z': spacing[2],
                        'voxel_size_unit': '\u03bcm',
                        'move_tiles_to_grid_(per_angle)?': '[Move Tile to Grid (Macro-scriptable)]',
                        'grid_type': '[Right & Down             ]',
                        'tiles_x': self._count_unique_positions(0),
                        'tiles_y': 1,
                        'tiles_z': 1,
                        'overlap_x_(%)': self._calculate_percent_overlap(),
                        'overlap_y_(%)': '10',
                        'overlap_z_(%)': '10',
                        'keep_metadata_rotation': None,
                        'how_to_load_images': '[Re-save as multiresolution HDF5]',
                        'dataset_save_path': '.',
                        'subsampling_factors': '[{ {1,1,1}, {2,2,2}, {4,4,4} }]',
                        'hdf5_chunk_sizes': '[{ {16,16,16}, {16,16,16}, {16,16,16} }]',
                        'timepoints_per_partition': '1',
                        'setups_per_partition': '0',
                        'use_deflate_compression': None,
                        'export_path': '../StitchedImages/dataset'
                }

                for key in provided_args:
                        args[key] = provided_args[key]

                return args

        def _get_spacing(self):
                """Get the spacing of the resulting image in microns"""
                lateral_spacing = self.acq_params['lateral resolution']
                axial_spacing = self.acq_params['axial resolution']
                elevational_spacing = self._calculate_position_separation(1)
                
                spacing = [lateral_spacing, axial_spacing, elevational_spacing]
                return spacing

        def _image_list_to_laterally_separate_3d_images(self, image_list):
                """
                Convert a list of 2d numpy arrays into 4d numpy array of laterally separate 3d images
                """
                image_array = np.array(image_list)
                shape_2d = np.shape(image_list[0])
                
                num_lateral = self._count_unique_positions(0)
                num_elevational = self._count_unique_positions(1)
                
                list_shape = [num_lateral, num_elevational, shape_2d[0], shape_2d[1]]
                array_of_3d_images = np.reshape(image_array, list_shape)
                
                return array_of_3d_images
                
        def _stitch_images_from_temporary_directory(self, array_of_images: np.ndarray):
                """
                Take a 4d array containing several 3D ultrasound images and stitch them externally through ImageJ
                """
                
                # todo: come up with alternate method for handling complex data
                # SITK can't handle complex data currently.
                if np.iscomplex(array_of_images).any():
                        print('Converting IQData to envelope data for stitching')
                        array_of_images = np.abs(array_of_images)
                
                try:
                        temp_dir = tempfile.mkdtemp()
                        self._write_images_to_temporary_dir(temp_dir, array_of_images)
                finally:
                        os.rmdir(temp_dir)

        def _write_images_to_temporary_dir(self, temp_dir, array_of_images):
                """Write 3d images, held in a 4d array, into temporary files with a consistent naming scheme"""
                num_images = len(array_of_images)
                for idx in range(num_images):
                        self._write_temp_image(array_of_images[idx], temp_dir, idx)
        
        def _write_temp_image(self, image_array, temp_dir, idx):
                """Write a 3D ultrasound image into a temporary file for use by ImageJ stitching"""
                temp_path = Path(temp_dir, 'UltrasoundImage_{}.tif'.format(idx))
                image = sitk.Cast(sitk.GetImageFromArray(image_array), sitk.sitkFloat32)
                image.SetSpacing(self._get_spacing())
                meta.write_image(image, temp_path)
        
        # Images
        def _mat_list_to_variable_list(self, variable):
                """Acquire a sorted list containing the specified variable in each mat file"""
                variable_list = [self.read_variable(file_path, variable) for file_path in self.mat_list]
                return variable_list
        
        # Positions
        def _read_position_list(self):
                """Open a Micromanager acquired position file and return a list of X, Y positions"""
                if self.pl_path is None:
                        return []

                acquisition_dict = util.read_json(self.pl_path)
                pos_list = clean_position_text(acquisition_dict)

                return pos_list

        @staticmethod
        def clean_position_text(acquisition_dict):
                """Convert a Micromanager acquired position file into a list of X, Y positions"""
                pos_list_raw = acquisition_dict['POSITIONS']
                pos_list = np.array([[row['DEVICES'][0]['X'], row['DEVICES'][0]['Y']]
                            for row in pos_list_raw])

                return pos_list
        
        def _count_unique_positions(self, axis):
                """Determine how many unique positions the position list holds along a particular axis"""
                num_unique = len(np.unique(self.pos_list[:, axis]))
                return num_unique
        
        def _calculate_position_separation(self, axis):
                """Check the distance between points along an axis"""
                unique = np.unique(self.pos_list[:, axis])
                
                if len(unique > 1):
                        separations = np.array([unique[i+1] - unique[i] for i in range(len(unique)-1)])
                        unique_separations = np.unique(separations)
                        
                        if len(unique_separations) > 1:
                                raise ValueError('There is more than one separation distance.  This grid is irregular')
                        
                        return np.abs(unique_separations[0])
                        
                else:
                        separation = 1
                
                return separation

        def _calculate_percent_overlap(self, transducer_fov=12800) -> int:
                """Calculate the percentage overlap between X images"""
                sep_lateral = self._calculate_position_separation(0)
                percent_sep = int(100 - 100 * (sep_lateral / transducer_fov))
                
                return percent_sep
        
        # List of files
        def _read_sorted_list_mats(self, search_str='.mat'):
                unsorted = util.list_filetype_in_dir(self.mat_dir, search_str)
                list_mats_sorted = sorted(unsorted, key=self.extract_iteration_from_path)
                return list_mats_sorted
        
        @staticmethod
        def extract_iteration_from_path(file_path):
                """Get the image index from filename formatted It-index.mat"""
                match = re.search(r'It-\d*', file_path.stem)
                index = int(match.group()[3:]) - 1
                return index

        # Parameters
        
        def _read_parameters(self, iq_path: Path):
                """
                Get the parameters from an acquisition and return a cleaned up dictionary
                """
                params = self.read_variable(iq_path, 'P')

                wl = params['wavelength_micron']
                # convert units to mm
                self.acq_params['lateral resolution'] = params['lateral_resolution'] * wl
                self.acq_params['axial resolution'] = params['axial_resolution'] * wl
                self.acq_params['transmit focus'] = params['txFocus'] * wl
                self.acq_params['start depth'] = params['startDepth'] * wl
                self.acq_params['end depth'] = params['endDepth'] * wl
                self.acq_params['transducer spacing'] = params['transducer_spacing'] * wl

                # copy other parameters that are not in wavelength
                self.acq_params['sampling wavelength'] = params['wavelength_micron']
                self.acq_params['speed of sound'] = params['speed_of_sound']

        @staticmethod
        def read_variable(file_path, variable):
                return util.load_mat(file_path, variables=variable)[variable]


class UltrasoundImage(sitk.Image):

        def get_bmode(self, compress_method='log'):
                """Get the stitched b-mode image"""
                if self.iq is None:
                        self.assemble_iq()

                if compress_method == 'log':
                        bmode = sitk.Log10(sitk.Abs(self.iq) + 1)
                elif compress_method == 'sqrt':
                        bmode = sitk.Sqrt(sitk.Abs(self.iq))
                else:
                        raise ValueError('Compression method can be log or sqrt, not {}'.format(compress_method))

                meta.copy_relevant_metadata(bmode, self.iq, self.metadata_keys)

                return bmode

        def get_envelope(self):
                """Get the stitched RF envelope image"""
                if self.iq is None:
                        self.assemble_iq()

                env = sitk.Abs(self.iq)
                meta.copy_relevant_metadata(env, self.iq, self.metadata_keys)

                return env

        def get_iq(self):
                if self.iq is None:
                        self.assemble_iq()

                return self.iq


def beamform_rf(raw_data):
        raise NotImplementedError('The function to beamform RF data has not been implemented yet')
# cases: 128 raylines, multiangle compounding,


def open_rf(rf_path: Path) -> np.ndarray:
        mat_data = sio.loadmat(str(rf_path))
        rf_data = beamform_rf(mat_data['RData'])
        
        return rf_data


def open_iq(iq_path: Path) -> np.ndarray:
        """Open a .mat that holds IQData and Parameters from the Verasonics system
    
        Input:
        A pathlib Path to an .mat file holding an 'IQData' variable, which is an array of complex numbers
    
        Output:
        iq_data: A numpy array of complex numbers, in (Z, X) indexing
        parameters: a dictionary
        """
        mat_data = sio.loadmat(str(iq_path))
        iq_data = mat_data['IQData']
        
        return iq_data


def open_parameters(iq_path: Path) -> dict:
        """Get the parameters from an acquisition and return a cleaned up dictionary"""
        mat_data = sio.loadmat(str(iq_path))
        param_raw = mat_data['P']
        parameters = format_parameters(param_raw)
        return parameters


def format_parameters(param_raw: np.ndarray) -> dict:
        """Format the parameters array loaded from matlab struct
    
        All numeric values are currently in units of wavelength"""
        parameters = {
                'Lateral resolution': np.double(param_raw['lateral_resolution']),
                'Axial resolution': np.double(param_raw['axial_resolution']),
                'speed of sound': np.double(param_raw['speed_of_sound']),
                'focus': np.double(param_raw['txFocus']),
                'start depth': np.double(param_raw['startDepth']),
                'end depth': np.double(param_raw['endDepth']),
                'transducer spacing': np.double(param_raw['transducer_spacing']),
                'sampling wavelength': np.double(param_raw['wavelength_micron'])
        }

        wavelength_to_mm = parameters['transducer spacing'] / 0.1

        # Convert to units of mm
        parameters['Lateral resolution'] = parameters['Lateral resolution'] / wavelength_to_mm
        parameters['Axial resolution'] = parameters['Axial resolution'] / wavelength_to_mm
        
        return parameters


def iq_to_bmode(iq_array: np.ndarray) -> np.ndarray:
        """Convert complex IQ data into bmode through squared transform"""
        env = np.abs(iq_array)
        bmode = np.log10(env + 1)
        
        return bmode


def clean_position_text(pos_text: dict) -> list:
        """Convert a Micromanager acquired position file into a list of X, Y positions"""
        pos_list_raw = pos_text['POSITIONS']
        pos_list = [[row['DEVICES'][0]['X'], row['DEVICES'][0]['Y']]
                    for row in pos_list_raw]
        
        return pos_list


def read_position_list(pl_path: Path) -> list:
        """Open a Micromanager acquired position file and return a list of X, Y positions"""
        with open(str(pl_path), 'r') as file_pos:
                text_pos = file_pos.read()
                dict_text = eval(text_pos)
                pos_list = clean_position_text(dict_text)
        
        return pos_list


def count_xy_positions(pos_list: list) -> (np.ndarray, np.ndarray, np.ndarray):
        """Determine how many unique Lateral and elevational positions the position list holds,
        as well as the physical separation """
        pos_array = np.array(pos_list)
        unique_lateral = np.unique(pos_array[:, 0])
        unique_elevational = np.unique(pos_array[:, 1])
        
        num_lateral_elevational = np.array([len(unique_lateral), len(unique_elevational)])
        
        if len(unique_lateral) > 1:
                lateral_sep = np.abs(unique_lateral[1] - unique_lateral[0])
        else:
                lateral_sep = 1
        
        if len(unique_elevational) > 1:
                elevational_sep = np.abs(unique_elevational[1] - unique_elevational[0])
        else:
                elevational_sep = 1
        
        return num_lateral_elevational, lateral_sep, elevational_sep


def index_from_file_path(file_path: Path) -> int:
        """Get the image index from filename formatted It-index.mat"""
        match = re.search(r'It-\d*', file_path.stem)
        index = int(match.group()[3:]) - 1
        return index


def get_sorted_list_mats(mats_dir: Path, search_str: str = 'mat') -> list:
        unsorted = util.list_filetype_in_dir(mats_dir, search_str)
        list_mats_sorted = sorted(unsorted, key=index_from_file_path)
        return list_mats_sorted


def get_idx_img_z(idx_raw: int, num_xy: np.ndarray, num_imgs: int) -> [int, int]:
        """Extract indexes for the 3D image and the elevational Z position of a mat file"""
        z_size = num_imgs / num_xy[0]
        idx_img = int(idx_raw / z_size)
        idx_z = np.mod(idx_raw, z_size)
        return int(idx_img), int(idx_z)


def mat_list_to_iq_array(mats_list: list) -> (np.ndarray, dict):
        """Make an IQ array from a list of mats"""
        parameters = open_parameters(mats_list[0])
        
        iq_array = np.array(
                [open_iq(x) for x in mats_list]
        )
        
        # todo: fix horizontal flipping in final image
        
        return iq_array, parameters


def mat_list_to_rf_array(mats_list: list) -> (np.ndarray, dict):
        """Make an RF array from a list of mats"""
        rf_array = np.array(
                [open_rf(x) for x in mats_list]
        )
        parameters = open_parameters(mats_list[0])
        
        return rf_array, parameters


def assemble_4d_envelope(mats_list: list, num_lateral_elevational: np.ndarray) -> (np.ndarray, dict):
        """Compile IQ Data US .mats into separate 3d images"""
        array_3d_multi_img, parameters = mat_list_to_iq_array(mats_list)
        array_3d_env = np.abs(array_3d_multi_img)
        shape_image = np.shape(array_3d_env[0, :, :])
        
        # [Image, Y (elevational), Z (axial), X (lateral)]
        shape_4d = [num_lateral_elevational[0], num_lateral_elevational[1], shape_image[0], shape_image[1]]
        array_4d = np.reshape(array_3d_env, shape_4d)
        
        return array_4d, parameters


def assemble_4d_bmode(mats_list: list, num_lateral_elevational: np.ndarray) -> (np.ndarray, dict):
        """Compile IQ Data US .mats into separate 3d images"""
        array_3d_multi_img, parameters = mat_list_to_iq_array(mats_list)
        array_3d_bmode = iq_to_bmode(array_3d_multi_img)
        shape_image = np.shape(array_3d_bmode[0, :, :])
        
        # [Image, Y (elevational), Z (axial), X (lateral)]
        shape_4d = [num_lateral_elevational[0], num_lateral_elevational[1], shape_image[0], shape_image[1]]
        array_4d = np.reshape(array_3d_bmode, shape_4d)
        
        return array_4d, parameters


def calculate_percent_overlap(x_sep: float) -> int:
        """Calculate the percentage overlap between X images"""
        percent_sep = int(100 - 100 * (x_sep / 12800))
        return percent_sep


def assemble_4d_data(mats_dir: Path, pl_path: Path, data_to_return: str = 'bmode') -> (np.ndarray, dict, int):
        list_mats = get_sorted_list_mats(mats_dir)
        list_pos = read_position_list(pl_path)
        num_lateral_elevational, lateral_separation, elevational_sep = count_xy_positions(list_pos)
        percent_overlap = calculate_percent_overlap(lateral_separation)
        
        if data_to_return == 'bmode':
                array_4d, parameters = assemble_4d_bmode(list_mats, num_lateral_elevational)
        elif data_to_return == 'envelope':
                array_4d, parameters = assemble_4d_envelope(list_mats, num_lateral_elevational)
        else:
                raise NotImplementedError

        parameters['Elevational resolution'] = elevational_sep / 1000
        
        return array_4d, parameters, percent_overlap


def write_image(img_array: np.ndarray, parameters: dict, output_path: Path):
        """
        Write a 3d US image with output spacing in mm
    
        :param img_array: Numpy array corresponding to the image
        :param parameters: Dictionary of parameters containing resolution keys
        :param output_path: output path to save the file to
        """
        image = sitk.GetImageFromArray(img_array)
        
        image_cast = sitk.Cast(image, sitk.sitkFloat32)
        
        spacing = np.array([parameters['Lateral resolution'], parameters['Axial resolution'],
                            parameters['Elevational resolution']])
        
        image_cast.SetSpacing(spacing)
        
        sitk.WriteImage(image_cast, str(output_path))


def stitch_elevational_image(mats_dir: Path, pl_path: Path, output_dir: Path, output_name: str,
                             data_to_return: str = 'bmode'):
        """Stitch and save images along the elevational direction.  Separate 3d images for each lateral position of stage
    
        :param mats_dir: directory holding the .mat files to be stitched
        :param pl_path: path to the position list file
        :param output_dir: directory where the images will be written to
        :param output_name: name of the output file
        :param data_to_return: type of us data to write, e.g. envelope data or bmode data.
        """
        separate_images_4d, parameters, percent_overlap = assemble_4d_data(mats_dir, pl_path, data_to_return)
        
        for idx in range(np.shape(separate_images_4d)[0]):
                path_output = Path(output_dir,
                                   output_name + '_Overlap-' + str(percent_overlap) + '_' + str(idx) + '.tif')
                write_image(separate_images_4d[idx], parameters, path_output)


def assemble_data_without_positions(mats_dir: Path, data_to_return: str = 'bmode') -> (np.ndarray, dict):
        """
    
        :param mats_dir: directory of iq files
        :param data_to_return: bmode or envelope of iq data
        :return: 3d array that doesn't consider position of data/no regular stitching
        """
        mats_list = get_sorted_list_mats(mats_dir)
        
        iq_array, parameters = mat_list_to_iq_array(mats_list)
        
        if data_to_return == 'bmode':
                img_array = iq_to_bmode(iq_array)
        elif data_to_return == 'envelope':
                img_array = np.abs(iq_array)
        else:
                raise NotImplementedError('This type of data has not been implemented yet')
        
        return img_array, parameters


def stitch_image_without_positions(mats_dir: Path, output_dir: Path, output_name: str, data_to_return: str = 'bmode',
                                   elevational_res=0.04):
        """
    
        :param mats_dir: directory holding the iq data .mat files
        :param output_dir: directory to write the final image to
        :param output_name: what to name the image
        :param data_to_return: type of us data to write, e.g. envelope data or bmode data.
        """
        array_img, parameters = assemble_data_without_positions(mats_dir, data_to_return)
        parameters['Elevational resolution'] = elevational_res
        
        path_output = Path(output_dir, output_name + '.tif')
        write_image(array_img, parameters, path_output)
