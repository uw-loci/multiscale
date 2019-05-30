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
                spacing = [get_spacing_tif(file_path, order[0]),
                           get_spacing_tif(file_path, order[1]),
                           get_spacing_tif(file_path, order[2])]
                
        return spacing
        

def get_spacing_tif(file_path, axis):
        with tif.TiffFile(str(file_path)) as tifr:
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
