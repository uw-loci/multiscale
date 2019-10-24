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
import multiscale.ultrasound.reconstruction as recon
import imagej
from pathlib import Path

ij = imagej.init('C:/users/mpinkert/Fiji.app/')

# stitch_dir = r'F:\Research\LINK' #
stitch_dir = r'C:\Users\mpinkert\Box\Research\LINK'

study_dir = 'Mouse images'
date = r'2019-10-21 - Mouse 210'
base_dir_list = ['L22 Fiducial Z16696']
#pl_path = Path(r'C:\Users\mpinkert\Box\Research\LINK\Phantom Trials\2019-05-04', '2019-05-04_US - 3X 100YSep.pos')
pl_path_base = Path(stitch_dir, study_dir, date)
runs = ['1']

for base_dir in base_dir_list:
        for run in runs:
                # pl_path = pl_path_base
                pl_path = Path(pl_path_base, base_dir + '.pos')
                #pl_path = Path(pl_path_base, 'Mouse 212 longitudinal.pos')
                mat_dir = Path(stitch_dir, study_dir, date, base_dir, 'Run-{}'.format(run))
                output_dir = Path(stitch_dir, study_dir, date,  base_dir)
                intermediate_save_dir = Path(stitch_dir, study_dir, date, base_dir,
                                             'Run-{} Intermediate'.format(run))
                output_name = base_dir + '_Run-{}.tif'.format(run)
                # pl_path = Path(r'F:\Research\LINK\Phantom Trials\2019-04-05\US_PositionList_25yspacing.pos')
                # pl_path = Path(r'F:\Research\LINK\Phantom Trials\2019-01-08\US_PositionLis_2019-01-08.pos')
        
                assembler = recon.UltrasoundImageAssembler(mat_dir, output_dir, ij, pl_path=pl_path,
                                                           intermediate_save_dir=intermediate_save_dir,
                                                           fuse_args={'downsampling': 2}, output_name=output_name)
                assembler.assemble_bmode_image(base_image_data='IQData')
