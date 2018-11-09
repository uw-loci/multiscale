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

import imagej
import numpy
from pathlib import Path
import tempfile
import os


class BigStitcher(object):
        """
        Image stitching using the BigStitcher ImageJ plugin
        """
        def __init__(self, ij):
                """Class for using the BigStitcher plugin on a python interface"""
                self._ij = ij

        def stitch_from_files(self, image_search_path, **kwargs):

                # Q: Enable interactive stitching with GUI if not in headless mode?
                # assemble files into dataset in save directory
                # stitch dataset

                return

        def stitch_from_numpy(self, images_np, **kwargs):
                try:
                        temp_dir = tempfile.mkdir()
                        self._save_images(images_np)
                        self.stitch_from_files(temp_dir, kwargs)
                finally:
                        os.rmdir(temp_dir)

                return

        def _save_images(self, files):
                # todo: save images in imagej.py
                return

        def _assemble_dataset(self, files_dir):
                return

        def _stitch_dataset(self):
                return