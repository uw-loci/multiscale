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

import numpy as np
import scipy.sparse as sp
import scipy.signal as sig
from pathlib import Path
from tqdm import tqdm

import multiscale.utility_functions as util
import multiscale.ultrasound.reconstruction as recon

class Beamformer(object):
        def __init__(self, rf_array: np.ndarray, params: dict, delays):
                self.rf_array = rf_array
                self.params = params
                self.delays = delays
                self.rf_vector = None
                
                self._format_rf()
                
        def _format_rf(self):
                """
                Reformat the rf data so that the rf data is interleaved properly and in a vector
                :return:
                """
                # Verasonics RF array is composed of two interleaved samples; however, the temporally first sample
                # occurs in the second half of the array.  This part corrects the array so that samples are interleaved
                # properly.
                temp_array = np.zeros(np.shape(self.rf_array))
                half_time = int(self.params['time samples'] / 2)
        
                temp_array[::2] = self.rf_array[half_time:]
                temp_array[1::2] = self.rf_array[:half_time]
        
                self.rf_vector = temp_array.flatten('F')
                
        def get_bmode(self):
                summation = self.delays @ self.rf_vector
                rf = np.reshape(summation, [self.params['axial samples'], self.params['lines']], order='F')
                iq = sig.hilbert(rf)
                bmode = recon.iq_to_db(iq)
                return bmode
                

class DelayCalculator(object):
        def __init__(self, params: dict, delays_path: Path):
                self.params = params
                self.delays_path = delays_path
                self.params_path = Path(self.delays_path.parent, self.delays_path.stem + '_params.json')
                self.delays = None
                
        def load_delays(self):
                if self.params_path.is_file():
                        self._read_delays()
                else:
                        print('No delay file found at {}.  Calculating new matrix.'.format(self.delays_path))
                        self._calculate_delays()
                        self._write_delays()
                        
        def get_delays(self):
                if self.delays is None:
                        self.load_delays()
                return self.delays

        def _calculate_delays(self):
                """
                The delay matrix is holds which samples contribute to a particular physical position.
                
                The delay matrix has (lines X axial sample) rows, and (time X transducer element) columns
                Each row is one physical position
                This is typically a sparse matrix
                
                NOTE: Numpy is in row-major format, meaning that columns/rows are reversed from matlab
                I.e., rows are element 0, columns element 1
                :return:
                """
                num_positions = self.params['axial samples']*self.params['lines']
                num_samples = self.params['time samples']*self.params['elements']
                time_indices = []
                position_indices = []
                for position in tqdm(range(num_positions)):
                        position_delays = self._position_delay(position)
                        time_indices.extend(position_delays)
                        
                        position_temp = [position]*len(position_delays)
                        position_indices.extend(position_temp)
                        
                time_indices = np.array(time_indices)
                position_indices = np.array(position_indices)
                weights = np.ones([len(time_indices)])
                
                self.delays = sp.csr_matrix((weights, (position_indices, time_indices)),
                                            shape=[num_positions, num_samples])
                                
        def _position_delay(self, position_idx):
                """
                Calculate the row
                :param position_idx:
                :return:
                """
                position_delays = list()
                for element in range(self.params['elements']):
                        element_delays = self._element_delay(position_idx, element)
                        position_delays.extend(element_delays)
                        
                return np.array(position_delays)
        
        def _element_delay(self, position_idx, element_idx) -> list:
                """
                Calculate which time samples from an element contribute to the position
                :param position_idx: Index corresponding to the position
                :param element_idx: Index of the element in question
                :return:
                """
                element_delays = []
                for transmit in range(self.params['elements']):
                        time_delay = self._time_delay(position_idx, element_idx, transmit)
                        element_delays.append(time_delay)
                                
                return element_delays
                
        def _time_delay(self, position_idx, element_idx, transmit):
                axial_index = position_idx % self.params['axial samples']
                axial_distance = axial_index * self.params['axial resolution']
                
                line = np.floor(position_idx/self.params['axial samples'])
                lat_point_to_transmit = transmit*self.params['transducer spacing'] \
                                        - line*self.params['lateral resolution']
                lat_point_to_element = element_idx*self.params['transducer spacing'] \
                                       - line*self.params['lateral resolution']
                dist_ptt = np.sqrt(axial_distance**2 + lat_point_to_transmit**2)
                dist_pte = np.sqrt(axial_distance**2 + lat_point_to_element**2)
                distance = dist_ptt + dist_pte
                
                time_delay = round((distance - self.params['start depth'])
                                   * self.params['sampling frequency'] / self.params['speed of sound']
                                   + transmit*self.params['transmit samples'])
                
                return time_delay
        
        def _write_delays(self):
                """
                Write a delays file that contains the delay matrix so as to reduce time cost
                :return:
                """
                sp.save_npz(str(self.delays_path), self.delays)
                params_path = Path(self.delays_path.parent, self.delays_path.stem + '_params.json')
                util.write_json(self.params, params_path)
        
        def _read_delays(self):
                """
                Find a delays file if it exists and read it in instead of calculating
                :return:
                """
                temp_params = util.read_json(self.params_path)
                if self.params == temp_params:
                        self.delays = sp.load_npz(self.delays_path)
                else:
                        raise("The parameters do not match.\n Point to the right file or to an unused file name")
