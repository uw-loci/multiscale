# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 09:40:25 2018

@author: mpinkert
"""

import multiscale.bulk_img_processing as blk
import multiscale.utility_functions as util
from pathlib import Path
import SimpleITK as sitk
import os
import numpy as np
import warnings


def three_d_to_rgb(image_3d):
        arr_rgb_wrong_idx = sitk.GetArrayFromImage(image_3d)
        if len(np.shape(arr_rgb_wrong_idx)) > 3:
                slice_not_empty = [np.mean(arr_rgb_wrong_idx[:, :, :, idx]) > 1 for idx in range(3)]
                idx_not_empty = np.where(slice_not_empty)[0][0]
                arr_rgb_wrong_idx_2 = arr_rgb_wrong_idx[:, :, :, idx_not_empty] + 0
                arr_rotated_idx = np.swapaxes(arr_rgb_wrong_idx_2, 0, 2)
                arr_correct_idx = np.swapaxes(arr_rotated_idx, 0, 1)
        else:
                arr_rotated_idx = np.swapaxes(arr_rgb_wrong_idx, 0, 2)
                arr_correct_idx = np.swapaxes(arr_rotated_idx, 0, 1)
        
        rgb_image = sitk.GetImageFromArray(arr_correct_idx, isVector=True)
        
        spacing_original = image_3d.GetSpacing()
        spacing_new = np.array([spacing_original[1], spacing_original[2]])
        rgb_image.SetSpacing(spacing_new)
        copy_relevant_metadata(rgb_image, image_3d)
        
        return rgb_image


def unit_to_factor_in_microns(unit: str)-> float:
        """
        Convert a string naming the unit of measure to its value in microns
        :param unit:
        :return:
        """
        if unit == 'microns':
                return 1.0
        
        if unit == 'millimeters':
                return 1.0E3
        
        if unit == 'centimeters:':
                return 1.0E4
        
        if unit == 'meters':
                return 1.0E6


def copy_relevant_metadata(new_image: sitk.Image, old_image: sitk.Image, necessary_keys: list=None):
        if necessary_keys is None:
                necessary_keys = ['Unit']
                
        for key in necessary_keys:
                try:
                        new_image.SetMetaData(key, old_image.GetMetaData(key))
                except:
                        warnings.warn('The {0} key does not exist'.format(key))
                
                
def convert_spacing_units(spacing: tuple, unit_workspace: str, unit_image: str):
        """
        Convert image spacing and unit between microns and millimeters
        :param spacing: Spacing of image to convert
        :param unit_workspace: Unit of workspace
        :param unit_image: unit of image
        :return: Correct spacing
        """
        if unit_workspace == unit_image:
                return spacing
        
        factor_workspace = unit_to_factor_in_microns(unit_workspace)
        factor_image = unit_to_factor_in_microns(unit_image)
        new_spacing = spacing * np.double((factor_workspace / factor_image))
        
        return new_spacing


def setup_image(path_image: Path, unit_workspace: str='microns', write_changes: bool=True, dimensions: int=2):
        """
        Read in an itk image and ensure that its spacing is in the right units/has been set in the first place
        :param path_image: path to the image file
        :param unit_workspace: unit that the workspace is working in
        :return:
        """
        image = sitk.ReadImage(str(path_image))
        metadata = read_metadata(path_image)
        
        if metadata is None:
                print('{0} has no metadata.'.format(str(path_image.name)))
                image.SetMetaData('Unit', unit_workspace)
                current_spacing = image.GetSpacing()
                change_spacing = util.query_yes_no('Change the spacing?  Current spacing is {0} >> '.format(current_spacing))
                
                if change_spacing:
                        spacing = util.query_float('Please enter the image spacing in {0} >> '.format(unit_workspace))
                        spacing_new = [spacing] * len(image.GetSpacing())
                        image.SetSpacing(spacing_new)
                        
                        if write_changes:
                                write_image(image, path_image)
                
        else:
                for key in metadata:
                        image.SetMetaData(key, metadata[key])
                
        if len(image.GetSpacing()) > dimensions:
                image = three_d_to_rgb(image)
                
        return image


def write_metadata(image_path: Path, image: sitk.Image):
        """Write down the metadata keys to a txt file"""
        metadata = {}
        for key in image.GetMetaDataKeys():
                metadata[key] = image.GetMetaData(key)
                
        metadata_path = Path(image_path.parent, image_path.stem + '_metadata.txt')
        util.write_json(metadata, metadata_path)


def read_metadata(image_path: Path):
        """Read a metadata dictionary from a file and return it, or return None if not found"""
        metadata_path = Path(image_path.parent, image_path.stem + '_metadata.txt')
        try:
                metadata = util.read_json(metadata_path)
                return metadata
        except:
                return None
        

def write_image(image: sitk.Image, image_path: Path):
        sitk.WriteImage(image, str(image_path))
        write_metadata(image_path, image)

        
# deprecated methods
def setup_image_from_csv(image_path, return_image=True, return_rotation=False, return_transform=True):
        """
        Set up the image spacing and optionally the registration origin
        
        This function is necessary because ITK cannot save in microns, making
        external metadata necessary.  It references, or creates, a csv file to
        handle this metadata
        
        Inputs:
        image_path -- The path to the image being setup
        setup_origin -- Set values for the origin or leaves at 0,0
        return_image -- Return the whole setup image
        return_spacing -- Return the spacing values
        
        Outputs:
        image -- The setup image if return_image is True
        spacing -- The spacing of the image if return_spacing is True
        
        """
        
        parameters = get_image_parameters(image_path)
        
        if return_image:
                image = sitk.ReadImage(str(image_path))
                
                if len(image.GetSpacing()) > 2:
                        image = three_d_to_rgb(image)
                
                spacing = parameters[0]
                origin = parameters[1]
                
                image.SetSpacing(spacing)
                
                if return_transform:
                        image.SetOrigin(origin)
                
                if return_rotation:
                        return image, parameters[2]
                else:
                        return image
        
        elif return_rotation:
                return parameters[2]


def get_image_parameters(image_path, return_spacing=True, return_origin=True,
                         return_rotation=True):
        file_path = str(image_path.parent) + '/Image Parameters.csv'
        
        image_parameters = blk.read_write_pandas_row(
                str(file_path), str(image_path.name),
                'Image', ['Spacing', 'X Origin', 'Y Origin', 'Rotation'])
        
        spacing = [float(image_parameters['Spacing']),
                   float(image_parameters['Spacing'])]
        
        origin = [float(image_parameters['X Origin']),
                  float(image_parameters['Y Origin'])]
        
        rotation = float(image_parameters['Rotation'])
        
        returns = []
        if return_spacing:
                returns.append(spacing)
        
        if return_origin:
                returns.append(origin)
        
        if return_rotation:
                returns.append(rotation)
        
        return returns


def write_image_parameters(image_path, spacing, origin, rotation=0):
        """Write down the spacing and origin of an image file to csv metadata"""
        
        (output_dir, image_name) = os.path.split(image_path)
        
        file_path = output_dir + '/Image Parameters.csv'
        
        column_labels = ['Spacing', 'X Origin', 'Y Origin', 'Rotation']
        
        column_values = [spacing[0], origin[0], origin[1], rotation]
        
        blk.write_pandas_row(file_path, image_name, column_values,
                             'Image', column_labels)
        
        

