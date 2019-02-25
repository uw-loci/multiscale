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
import scipy.stats as scist


def fisher_transformation(correlation):
        """
        Calculate the Z score of a correlation coefficient using the fisher transformation
        
        :param correlation: Pearson's correlation coefficient value, or series of values
        :return: Z
        """
        return np.arctanh(correlation)


def inverse_fisher_transform(z):
        """
        
        :param z: The Z value of a correlation coefficient
        :return: The Pearson correlation coefficient corresponding to Z
        """
        return np.tanh(z)


def z_standard_error(n):
        """
        Calculate the standard error of a Z score
        :param n: Number of samples
        :return: Standard error of Z
        """
        if n < 4:
                print('Warning: n less than 4 for a calculation.  Returning a SE of 2.')
                return 2
                
        return np.sqrt(1/(n-3))


def pooled_z_se(n_values):
        """
        Calculate the standard error of multiple Z values
        :param n_values: Number of samples in each Z value
        :return: Pooled standard error of Z value
        """
        se2_individual = []
        for n in n_values:
                se2_individual.append(np.square(z_standard_error(n)))
                
        se2 = np.sum(se2_individual)
        se = np.sqrt(se2)
        return se
        

def mean_correlation(correlations):
        """
        Calculate the mean
        :param correlations:
        :return:
        """
        z = fisher_transformation(correlations)
        zbar = np.mean(z)
        rbar = inverse_fisher_transform(zbar)
        
        return rbar
    
        
def p_value(z_scores, two_tailed=True):
        if two_tailed:
                p_values = scist.norm.sf(abs(z_scores)) * 2
        else:
                p_values = scist.norm.sf(abs(z_scores))  # one-sided

        return p_values
        

def correlation_t_test(corr1, n1, corr2, n2, two_tailed=True):
        """
        Calculate the p value of two correlations being different
        :param corr1: The first correlation
        :param n1: Samples used to calculate the first correlation
        :param corr2: The second correlation
        :param n2: Samples used to calculate the second correlation
        :param two_tailed: Whether to return the two tailed (default) or one tailed p value
        :return:
        """
        z1 = fisher_transformation(corr1)
        z2 = fisher_transformation(corr2)
        
        se_pooled = pooled_z_se(np.array([n1, n2]))
        
        z = (z1-z2)/se_pooled
        p = p_value(z, two_tailed)
        return p


def z_t_test(z1, se1, z2, se2, two_tailed=True):
        """
        Perform a t test between two Z values
        :param z1: First Z value
        :param se1: Standard error of z1
        :param z2: Second Z value
        :param se2: standard error of z2
        :param two_tailed: True if two tailed t test, False if one tailed
        :return: p value
        """
        se2_individual = np.square([se1, se2])
        se2 = np.sum(se2_individual)
        se = np.sqrt(se2)
        
        z = (z1-z2)/se
        
        p = p_value(z, two_tailed)
        return p

