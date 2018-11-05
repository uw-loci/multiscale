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
import xml

#
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