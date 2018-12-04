"""
This module handles writing/converting image data into the big data viewer HDF5 and XML formats.

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
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
import h5py
from pathlib import Path
import re


class BigViewerDatasetWriter(object):
        def __init__(self, dataset_name=None, output_dir=None):
                self.datset_name = dataset_name
                self.output_dir = output_dir

        def set_dataset_name(self, dataset_name):
                self.datset_name = dataset_name

        def set_output_dir(self, output_dir):
                self.output_dir = output_dir

        def _create_new_dataset(self):
                return

        def _append_to_dataset(self):
                return





def calculate_affine_transform(spacing):
        return

def write_dataset_xml(position_list_with_metadata, output_dir, output_name):
        return


def append_new_setup_to_dataset_xml():
        return

# deprecated due to being able to call run with 4 arguments, the 4th a dict, but not yet deleting

def assemble_run_statement(function_call: str, arg_dict=None, ij1_style=True):
        """
        Assemble an ImageJ macro string given a plugin to run and optional arguments in a dict
        :param function_call: The string call for the function to run
        :param arg_dict: A dict of macro arguments in key/value pairs
        :param ij1_style: Whether to use implicit booleans in IJ1 style or explicit booleans in IJ2 style
        :return: A string version of the macro run
        """
        if arg_dict is None:
                macro = "run(\"{}\");".format(function_call)
                return macro
        macro = """run("{0}", \"""".format(function_call)
        for key, value in arg_dict.items():
                argument = _format_argument(key, value, ij1_style)
                if argument is not None:
                        macro = macro + ' {}'.format(argument)
        macro = macro + """\");"""
        return macro

def _format_argument(key, value, ij1_style):
        if value is True:
                argument = '{}'.format(key)
                if not ij1_style:
                        argument = argument + '=true'
        elif value is False:
                argument = None
                if not ij1_style:
                        argument = '{0}=false'.format(key)
        elif value is None:
                raise NotImplementedError('Conversion for None is not yet implemented')
        else:
                val_str = _format_value(value)
                argument = '{0}={1}'.format(key, val_str)
        return argument

def _format_value(value):
        temp_value = str(value).replace('\\', '/')
        if temp_value.startswith('[') and temp_value.endswith(']'):
                return temp_value
        final_value = '[' + temp_value + ']'
        return final_value
