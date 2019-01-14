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


class Beamformer(object):
        def __init__(self, rf_array, params):
                self.rf_array = rf_array
                self.rf_vector = None
                self.params = params
                self.delays = None
                
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
                self.delays = sp.csr_matrix([self.params['axial samples']*self.params['lines'],
                                        self.params['time samples']*self.params['elements']])
                
        def _position_delay(self, position_idx):
                """
                Calculate the row
                :param position_idx:
                :return:
                """
                delay = np.zeros(self.params['time samples']*self.params['elements'])
                for element in range(self.params['elements']):
                        element_contribution = self._element_delay(position_idx, element)
                        for time_index, weight in element_contribution.iteritems():
                                delay[time_index] = weight
                                
                return delay
                
        def _element_delay(self, position_idx, element_idx) -> dict:
                """
                Calculate which time samples from an element contribute to the position
                :param position_idx: Index corresponding to the position
                :param element_idx: Index of the element in question
                :return:
                """
                contributions = {}
                for transmit in range(self.params['elements']):
                        acq_contribution = self._time_delay(position_idx, element_idx, transmit)
                        for time_index, weight in acq_contribution:
                                contributions[time_index] = weight
                
        def _time_delay(self, position_idx, element_idx, transmit):
                axial_distance = position_idx % self.params['axial samples']
                line = np.floor(position_idx/self.params['axial samples'])
                lat_distance = element_idx*self.params['transducer spacing'] - line*self.params['lateral resolution']
                distance = np.sqrt(axial_distance**2 + lat_distance**2)
                
                time_in_samples = (distance - self.params['start depth']) \
                                  * self.params['sampling frequency'] / self.params['speed of sound']
                
                if float(time_in_samples).is_integer():
                        return {time_in_samples: 1}
                else:
                        weight_1 = time_in_samples % 1
                        weight_2 = 1 - weight_1
                        return {np.floor(time_in_samples): weight_1,
                                np.ceil(time_in_samples): weight_2}
                
        def _format_rf(self):
                """
                Reformat the rf data so that the rf data is interleaved properly and in a vector
                :return:
                """
                # Verasonics RF array is composed of two interleaved samples; however, the temporally first sample
                # occurs in the second half of the array.  This part corrects the array so that samples are interleaved
                # properly.
                temp_array = np.zeros(np.shape(self.rf_array))
                half_time = self.params['time samples']/2
                
                temp_array[::2] = self.rf_array[half_time:]
                temp_array[1::2] = self.rf_array[:half_time]
                
                self.rf_vector = temp_array.flatten('F')
                
        def _write_delays(self):
                """
                Write a delays file that contains the delay matrix so as to reduce time cost
                :return:
                """
                return
        
        def _read_delays(self):
                """
                Find a delays file if it exists and read it in instead of calculating
                :return:
                """
                return
                
