"""
Script to beamform a single frame of RF data for testing and quick visuals

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
import matplotlib.pyplot as plt
import multiscale.ultrasound.reconstruction as recon
import multiscale.ultrasound.beamform as beam

rf_path = Path(r'F:\Research\LINK\Phantom Trials\2019-01-17\Glass dish water\Run-3',
               'Smaller glass 2.mat')
output_dir = Path(r'F:\Research\LINK\Phantom Trials\2019-01-17')
delays_path = Path(output_dir, 'Delay matrix 2.npz')

params = recon.read_parameters(rf_path)
rf_array = recon.read_variable(rf_path, 'RData')

delay_calculator = beam.DelayCalculator(params, delays_path)
delays = delay_calculator.get_delays()

beamformer = beam.Beamformer(rf_array, params, delays)
bmode = beamformer.get_bmode()

plt.imshow(bmode, cmap='Greys')
plt.show()
print('Hello world')





