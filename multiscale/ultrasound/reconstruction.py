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
import multiscale.imagej.stitching as st
import os
import tiffile as tif
import warnings

class UltrasoundImageAssembler(object):
        """
        todo: start generalizing this so it can work with multiple image types/kinds
        """
        def __init__(self, mat_dir: Path, output_dir: Path, ij=None, pl_path: Path=None,
                     intermediate_save_dir: Path=None, dataset_args: dict=None, fuse_args: dict=None,
                     search_str: str='.mat', output_name='fused_tp_0_ch_0.tif', params_path=None,
                     overwrite_dataset=None, overwrite_tif=None):
                """
                Class for assembling a 3D Ultrasound image taken with the LINK imaging system
                :param mat_dir: Directory holding the Verasonics generated .mat files
                :param output_dir: Directory to print the end image
                :param ij: A PyImageJ instance with the BigStitcher plugin
                :param pl_path: Path to the OpenScan generated position list
                :param intermediate_save_dir: Place to save the dataset used by BigStitcher.
                :param dataset_args: Alternative arguments for creating the BigStitcher dataset.
                :param fuse_args: Alternative arguments for fusing the BigStitcher dataset.
                :param search_str: A string at the end of the file that identifies which .mats are used from mat_dir.
                :param output_name: What to save the resulting image as.  Default is BigStitcher's default
                :param params_path: Path to a Verasonics settings file
                :param overwrite_dataset: Whether to overwrite an intermediate dataset that already exists
                :param overwrite_tif: Whether to overwrite a final tif if it already exists.
                """

                self.mat_dir = mat_dir
                self.pl_path = pl_path
                self.output_dir = output_dir
                self._ij = ij
                self.intermediate_save_dir = intermediate_save_dir
                self.output_name = output_name

                if intermediate_save_dir:
                        os.makedirs(str(intermediate_save_dir), exist_ok=True)

                os.makedirs(str(output_dir), exist_ok=True)
                
                self.search_str = search_str
                self.pos_list, self.pos_labels = self._read_position_list()
                
                self.mat_list = self._read_sorted_list_mats()
                if params_path == None:
                        self.params = read_parameters(self.mat_list[0])
                else:
                        self.params = read_parameters(params_path)

                self.fuse_args = self._assemble_fuse_args(fuse_args)
                self.dataset_args = self._assemble_dataset_arguments(dataset_args)
                self.overwrite_dataset = overwrite_dataset
                self.overwrite_tif = overwrite_tif

        def get_acquisition_parameters(self):
                """Get the US acquisition parameters"""
                return self.params
        
        def _convert_to_2d_tiffs(self):
                """Convert US slices to individual 2D tifs"""
                image_list = self._mat_list_to_variable_list('IQData')
                for idx in range(len(self.pos_labels)):
                        file_name = 'US_' + self.pos_labels[idx] + '.tif'
                        bmode = self._iq_to_output(image_list[idx])
                        self._save_us_image(file_name, bmode)
                        
        def _save_us_image(self, file_name, bmode):
                """
                Save a 3D US image as a tif
                :param file_name: Name of the output file
                :param bmode: The 3D image to save
                :return:
                """
                path = str(Path(self.output_dir, file_name))
                print('Saving {}'.format(path))
                spacing = self._get_spacing()
                ijstyle = bmode.astype(np.float32)
                shape = ijstyle.shape
                ijstyle.shape = 1, shape[0], 1, shape[1], shape[2], 1
                
                tif.imwrite(path, ijstyle, imagej=True,
                            resolution=(1./self.params['lateral resolution'], 1./self.params['axial resolution']),
                            metadata={'spacing': spacing[2], 'unit': 'um'})
                
                print('Finished saving {}'.format(path))
        
        def assemble_bmode_image(self, base_image_data='IQData'):
                """
                Stitch the .mat based ultrasound image into a bmode and save the results
                :param base_image_data: The variable being stitched in the .mat files
                :return:
                """
                
                if self._check_for_output():
                        return
                
                if self._check_for_xml():
                        stitcher = st.BigStitcher(self._ij)
                        # todo: fix so that this checks for existing files properly
                        stitcher._fuse_dataset(self.fuse_args, self.output_name)
                        return
                
                image_list = self._mat_list_to_variable_list(base_image_data)
                if len(self.pos_list) == 0 or self._count_unique_positions(0) == 1:
                        image_array = np.array(image_list)
                        bmode = iq_to_bmode(image_array)
                        self._save_us_image(self.output_name, bmode)
                else:
                        separate_3d_images = self.\
                                _image_list_to_laterally_separate_3d_images(image_list)
                        bmode = iq_to_bmode(separate_3d_images)
                        self._stitch_image(bmode)

        def assemble_qus_image(self, base_image_data='param_map'):
                """
                Stitch the .mat based ultrasound image and save the results
                :param base_image_data: The variable being stitched in the .mat files
                :return:
                """
        
                if self._check_for_output():
                        return
        
                if self._check_for_xml():
                        stitcher = st.BigStitcher(self._ij)
                        # todo: fix so that this checks for existing files properly
                        stitcher._fuse_dataset(self.fuse_args, self.output_name)
                        return
        
                image_list = self._mat_list_to_variable_list(base_image_data)
                if len(self.pos_list) == 0 or self._count_unique_positions(0) == 1:
                        image_array = np.array(image_list).astype(np.float32)
                        self._save_us_image(self.output_name, image_array)
                else:
                        separate_3d_images = self. \
                                _image_list_to_laterally_separate_3d_images(image_list)
                        self._stitch_image(separate_3d_images)
                        
        def _check_for_output(self):
                output_path = Path(self.fuse_args['output_file_directory'].replace('[', '').replace(']', ''),
                                   self.output_name)
                if output_path.is_file():
                        if self.overwrite_tif is not None:
                                return self.overwrite_tif
                        else:
                                return util.query_yes_no(
                                        '{} already exists.  Skip image fusion? >> '.format(output_path))
                else:
                        return False
                        
                        
        def _check_for_xml(self):
                """
                Check for the dataset.xml file and ask if the user wants to skip reading/resaving the .mat files.
                
                :return: boolean whether to skip dataset definition or not.
                """
                if self.intermediate_save_dir is not None:
                        xml_path = Path(self.intermediate_save_dir, 'dataset.xml')
                        if xml_path.is_file():
                                if self.overwrite_dataset is None:
                                        return util.query_yes_no(
                                                'XML file already exists.  Skip reading .mat files? >> ')
                                else:
                                        return self.overwrite_dataset
                else:
                        return False
        
        def _stitch_image(self, bmode):
                """
                Stitch the image using the BigStticher plugin
                :param bmode: the 4D array (3 dimensions + lateral tiles) bmode of the US
                :return:
                """
                
                if self.dataset_args['overlap_x_(%)'] is None:
                        self._save_us_image(self.output_name, bmode[0])
                        return
                        
                stitcher = st.BigStitcher(self._ij)
                stitcher.stitch_from_numpy(bmode, self.dataset_args, self.fuse_args,
                                           intermediate_save_dir=self.intermediate_save_dir,
                                           output_name=self.output_name)
        
        def _assemble_dataset_arguments(self, input_args):
                spacing = self._get_spacing()
                args = {
                        'define_dataset': '[Automatic Loader (Bioformats based)]',
                        'project_filename': 'dataset.xml',
                        'exclude': '10',
                        'pattern_0': 'Tiles',
                        'modify_voxel_size?': True,
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
                        'keep_metadata_rotation': True,
                        'how_to_load_images': '[Load raw data]',
                        'dataset_save_path': str(self.intermediate_save_dir),
                        'subsampling_factors': '[{ {1,1,1}, {2,2,2}, {4,4,4} }]',
                        'hdf5_chunk_sizes': '[{ {16,16,16}, {16,16,16}, {16,16,16} }]',
                        'timepoints_per_partition': '1',
                        'setups_per_partition': '0',
                        'use_deflate_compression': True,
                        'export_path': str(self.intermediate_save_dir) + '/dataset'
                }
                if input_args is not None:
                        for key, value in input_args.items():
                                args[key] = value
                                
                return args
        
        def _assemble_fuse_args(self, input_args):
                xml_path = str(self.intermediate_save_dir) + '/dataset.xml'
                
                args = {
                        'select': xml_path,
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
                        'blend': True,
                        'preserve_original': True,
                        'produce': '[Each timepoint & channel]',
                        'fused_image': '[Save as (compressed) TIFF stacks]',
                        'output_file_directory': str(self.output_dir)
                }
                if input_args is not None:
                        for key, value in input_args.items():
                                args[key] = value
        
                return args

        def _get_spacing(self):
                """Get the spacing of the resulting image in microns"""
                lateral_spacing = self.params['lateral resolution']
                axial_spacing = self.params['axial resolution']
                try:
                        elevational_spacing = self._calculate_position_separation(1)
                except TypeError:
                        elevational_spacing = np.max([lateral_spacing, axial_spacing])
                        warning = 'No elevational spacing found. Setting to max of lateral and axial: {}'.format(
                                elevational_spacing)
                        warnings.warn(warning)
                
                spacing = [lateral_spacing, axial_spacing, elevational_spacing]
                return spacing

        def _image_list_to_laterally_separate_3d_images(self, image_list):
                """
                Convert a list of 2d numpy arrays into 4d numpy array of laterally separate 3d images
                """
                # todo: check for multiple angles and select middle angle if exists?
                image_array = self._get_2d_array(np.array(image_list))
                shape_2d = np.shape(image_array[0])
                
                num_lateral = self._count_unique_positions(0)
                num_elevational = self._count_unique_positions(1)
                
                list_shape = [num_lateral, num_elevational, shape_2d[0], shape_2d[1]]
                array_of_3d_images = np.reshape(image_array, list_shape)
                
                return array_of_3d_images

        def _get_2d_array(self, image_list):
                """
                Return a list of 2D IQ data arrays, defaulting to the middle angle and first frame
                
                :param image_list: list of each IQData array from the .mat files
                :return: image_array: A 3D numpy array corresponding to a list of 2D IQ images
                """
                shape = np.shape(image_list[0])
                dims = np.size(shape)
                if dims == 3:
                        image_array = np.array(image_list[:, :, :, np.int(np.floor(shape[2] / 2))])
                elif dims == 5:
                        image_array = np.array(image_list[:, :, :, np.int(np.floor(shape[2] / 2)), 1, 1])
                elif dims == 2:
                        image_array = np.array(image_list)
                else:
                        raise(NotImplementedError, 'Image conversion not implemented for this {} IQ dimensions'.format(dims))
                
                return image_array
        # Images
        def _mat_list_to_variable_list(self, variable):
                """Acquire a sorted list containing the specified variable in each mat file"""
                variable_list = [read_variable(file_path, variable) for file_path in self.mat_list]
                return variable_list
        
        # Positions
        def _read_position_list(self):
                """Open a Micromanager acquired position file and return a list of X, Y positions"""
                if self.pl_path is None:
                        return [], []

                acquisition_dict = util.read_json(self.pl_path)
                return clean_position_text(acquisition_dict)
        
        def _count_unique_positions(self, axis):
                """Determine how many unique positions the position list holds along a particular axis"""
                num_unique = len(np.unique(self.pos_list[:, axis]))
                return num_unique
        
        def _calculate_position_separation(self, axis):
                """Check the distance between points along an axis"""
                unique = np.unique(self.pos_list[:, axis])
                
                if len(unique) > 1:
                        separations = np.array([unique[i+1] - unique[i] for i in range(len(unique)-1)])
                        unique_separations = np.unique(separations)
                        
                        if len(unique_separations) > 1:
                                if not util.list_values_approx_equal(unique_separations, 1E-3):
                                        raise ValueError('There is more than one separation distance.' \
                                                         + ' This grid is irregular\n' \
                                                         + str(unique_separations))
                        
                        return np.abs(unique_separations[0])
                        
                else:
                        separation = None
                
                return separation

        def _calculate_percent_overlap(self, transducer_fov=12800) -> int:
                """Calculate the percentage overlap between X images"""
                try:
                        transducer_fov = self.params['line samples']*self.params['lateral resolution']
                except KeyError:
                        print('Could not calculate transducer FOV.  Parameter missing.  Using default of 12.8 mm')
                finally:
                        try:
                                sep_lateral = self._calculate_position_separation(0)
                                percent_sep = int(100 - 100 * (sep_lateral / transducer_fov))
                        except:
                                percent_sep = None
                
                return percent_sep
        
        # List of files
        def _read_sorted_list_mats(self):
                unsorted = util.list_filetype_in_dir(self.mat_dir, self.search_str)
                list_mats_sorted = sorted(unsorted, key=extract_iteration_from_path)
                return list_mats_sorted

        # Parameters
        
        
def read_parameters(mat_path: Path) -> dict:
        """
        Get the parameters from an acquisition and return a cleaned up dictionary
        """
        params_raw = read_variable(mat_path, 'P')
        params = {}
        
        wl = params_raw['wavelength_micron']
        # convert units to micron
        params['lateral resolution'] = params_raw['lateral_resolution'] * wl
        params['axial resolution'] = params_raw['axial_resolution'] * wl
        params['transmit focus'] = params_raw['txFocus'] * wl
        params['start depth'] = params_raw['startDepth'] * wl
        params['end depth'] = params_raw['endDepth'] * wl
        params['transducer spacing'] = params_raw['transducer_spacing'] * wl
        params['speed of sound'] = params_raw['speed_of_sound']*1E6

        # copy other parameters that are not in wavelengths
        params['sampling wavelength'] = params_raw['wavelength_micron']
        
        try: # Necessary to have a try to allow processing older images
                params['raylines'] = params_raw['numRays']
                params['sampling frequency'] = params_raw['sampling_frequency'] * 1E6
                params['axial samples'] = params_raw['axial_samples']
                params['transmit samples'] = params_raw['transmit_samples']
                params['time samples'] = params_raw['time_samples']
                params['elements'] = params_raw['elements']
                params['element sensitivity'] = params_raw['element_sensitivity']
                params['line samples'] = params_raw['line_samples']

        finally:
                return params


def read_variable(file_path, variable):
        return util.load_mat(file_path, variables=variable)[variable]


def clean_position_text(pos_text: dict) -> (np.ndarray, list):
        """Convert a Micromanager acquired position file into a list of X, Y positions"""
        pos_list_raw = pos_text['POSITIONS']
        pos_list = [[row['DEVICES'][0]['X'], row['DEVICES'][0]['Y']]
                    for row in pos_list_raw]
        pos_labels = [row['LABEL'] for row in pos_list_raw]
        
        return np.array(pos_list), pos_labels


def extract_iteration_from_path(file_path):
        """Get the image index from filename formatted It-index.mat"""
        match = re.search(r'It-\d*', file_path.stem)
        index = int(match.group()[3:]) - 1
        return index


def iq_to_db(image_array):
        db = 20 * np.log10(np.abs(image_array) + np.min(np.abs(image_array))*0.001)
        return db.astype('f')


def get_origin(pl_path, params_path, gauge_value):
        """
        Get the coordinate system origin for the US image
        :param pl_path: Path to the position list for the acquisition
        :param params_path: Path to a .mat file containing the P parameter struct
        :param gauge_value: Value of the indicator gauge
        :return: Origin in X, Y, Z
        """
        params = read_parameters(params_path)
        origin_xy = get_xy_origin(pl_path)
        origin_z = get_z_origin(params, gauge_value)
        origin = [origin_xy[0], origin_xy[1], origin_z]
        return origin


def get_xy_origin(pl_path, params=None):
        """Read an micromanager position list and get the XY origin"""
        raw_pos_list = util.read_json(pl_path)
        pos_list = clean_position_text(raw_pos_list)[0]
        xy_origin = np.min(pos_list, 0)
        if params is not None:
                xy_origin[0] = xy_origin[0] - 0.5*params['raylines']*params['transducer spacing']
        
        return xy_origin


def get_z_origin(params, gauge_value):
        """
        Get the Z coordinate origin of the US system
        :param params: Parameters of the acquisition
        :param gauge_value: Indicator gauge value
        :return: Z coordinate
        """
        image_origin = params['start depth'] + params['axial samples']*params['axial resolution']
        z_origin = image_origin + gauge_value
        return z_origin



"""
Deprecated methods

To be gradually removed from use
"""
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
        bmode = 20*np.log10(env + 1)
        
        return bmode


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
