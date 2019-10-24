"""
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
from pathlib import Path

import SimpleITK as sitk
import tiffile as tif
import numpy as np
import warnings


def get_positions(file_path):
        """Read a .ome.tif file and grab the image positions as a numpy array"""
        info = get_info(file_path)
        mpm_list = []
        for position in info['OME']['Image']:
                x = position['StageLabel']['X']
                y = position['StageLabel']['Y']
                z = position['Pixels']['Plane'][0]['PositionZ']
                mpm_list.append(np.array([x, y, z]))
        return np.array(mpm_list)


def get_spacing(file_path, order=None):
        """
        Get the spacing from an .ome.tif file and return it in X, Y, Z order
        :param file_path: Path to the file
        :param order: List containing the order of the X, Y, and Z axes in the image, if they differ from [X, Y, Z]
        :return: Spacing as a list
        """
        if order is None:
                order = ['X', 'Y', 'Z']
        try:
                info = get_info(file_path)
                pixel_info = info['OME']['Image'][0]['Pixels']
                spacing = [pixel_info['PhysicalSize' + order[0]],
                           pixel_info['PhysicalSize' + order[1]],
                           pixel_info['PhysicalSize' + order[2]]]
        except:
                spacing = [1, 1, 1]
                warnings.warn('Could not read the spacing.  Spacing has been set to 1, 1, 1.  Fix manually', )

        return spacing
        

def get_spacing_tif(file_path, axis):
        with tif.TiffFile(str(file_path)) as tifr:
                tifr.pages[0].tags
                try:
                        if axis == 'X' or axis == 'Y':
                                spacing = tifr.pages[0].tags[axis + 'Resolution'].value[1]
                        elif axis == 'Z':
                                spacing = tifr.imagej_metadata['spacing']
                        else:
                                raise NotImplementedError(
                                        'Getting spacing along {} is not yet implemented'.format(axis))
                except:
                        # todo: Find a way to extract spacing from BigStitcher stitched images
                        spacing = 1
                        warnings.warn('Could not read the spacing.  Spacing has been set to 1, 1, 1.  Fix manually', )
                        
                return spacing


def get_info(file_path):
        """
        Get the XML data as a dictionary from a .ome.tif file.
        :param file_path: Path to the file.
        :return: XML data as dict
        """
        reader = sitk.ImageFileReader()
        reader.SetFileName(str(file_path))
        reader.ReadImageInformation()
        raw_info = reader.GetMetaData('ImageDescription')
        return tif.xml2dict(raw_info)


def save_ijstyle_overlay(images_list: list, save_path: Path):
        """
        Save a list of images as a tif, with each image a channel
        :param images_list: List of SimpleITK images of the same shape, spacing, and dtype
        :param save_path: File path to save at
        :return:
        """
        spacing = images_list[0].GetSpacing()
        overlay = sitk_to_ijstyle_overlay(images_list)
        save_ijstyle(overlay, save_path, spacing)


def save_ijstyle(img, save_path, spacing, unit='um'):
        """
        Save an image with the ijstyle using tiffile
        :param img: numpy array in TZCYXS order
        :param save_path: File path to save it
        :param spacing: [x, y, z] spacing
        :param unit: Unit used for the spacing.  Default um for micrometers
        :return:
        """
        tif.imwrite(save_path, img, imagej=True,
                    resolution=(1. / spacing[0], 1. / spacing[1]),
                    metadata={'spacing': spacing[2], 'unit': unit})


def sitk_to_ijstyle_overlay(images_list):
        """
        Overlay a list of SimpleITK images into the ImageJ style, where each image is a channel
        :param images_list: List of SimpleITK images.
        :return: The ImageJ style overlay in TZCYXS order
        """
        arr_list = [sitk_to_ijstyle(img) for img in images_list]
        
        num_images = len(arr_list)
        
        shape = arr_list[0].shape
        dtype = arr_list[0].dtype
        spacing = images_list[0].GetSpacing()
        
        for idx in range(num_images):
                if shape != arr_list[idx].shape:
                        raise Exception(
                                'Image 0 and Image {} are not the same size.  They cannot be overlaid'.format(idx + 1))
                elif dtype != arr_list[idx].dtype:
                        raise Exception(
                                'Image 0 and Image {} do not have the same pixel type.  They cannot be overlaid'.format(idx + 1))
                elif spacing != images_list[idx].GetSpacing():
                        raise Exception(
                                'Image 0 and Image {} do not have the same spacing.  They cannot be overlaid'.format(idx + 1))

        overlay = np.zeros([shape[0], shape[1], num_images, shape[3], shape[4]], arr_list[0].dtype)
        for idx in range(num_images):
                overlay[:, :, idx, :, :] = np.squeeze(arr_list[idx][:, :, 0, :, :], 4)
        
        return overlay


def sitk_to_ijstyle(img):
        """
        Convert a SimpleITK image into an ijstyle array for saving with tiffile
        :param img: SimpleITK image
        :return: IJ style array in TZCXYS order.
        """
        arr = sitk.GetArrayFromImage(img)
        if arr.dtype != np.uint8:
                arr = arr.astype(np.float32)
        
        shape = arr.shape
        arr.shape = 1, shape[0], 1, shape[1], shape[2], 1
        
        return arr