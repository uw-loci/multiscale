"""
A module for image stitching using the ImageJ interface.
"""
import imagej
import numpy
from pathlib import Path


class BigStitcher(object):
        """
        Image stitching using the BigStitcher ImageJ plugin
        """
        def __init__(self, ij):
                """Class for using the BigStitcher plugin on a python interface"""
                self._ij = ij

        def stitch_from_files(self, image_search_path, **kwargs):
                # assemble temporary files into dataset in save directory
                # stitch dataset

                return

        def stitch_from_numpy(self, images_np, **kwargs):
                # save temporary files using ImageJ
                # assemble temporary files into dataset in save directory
                # stitch dataset
                return