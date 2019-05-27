# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 09:25:11 2018

@author: mpinkert
"""
import matplotlib.pyplot as plt
import numpy as np


def auto_window_level(arr: np.array, bins=200, upper_limit_fraction=0.1, lower_limit_fraction=0.0002,
                      return_image=True):
        """Automatically window/level based on the image histogram"""
        hist, bin_edges = np.histogram(arr, bins=bins)
        bin_size = bin_edges[1] - bin_edges[0]
        
        if lower_limit_fraction > upper_limit_fraction:
                print('Invalid upper and lower pixel fractions.  Returning input array.')
                return arr
        
        upper_threshold_pixels = np.size(arr)*upper_limit_fraction
        lower_threshold_pixels = np.size(arr)*lower_limit_fraction
        
        hist_lower_limit = 0
        hist_upper_limit = len(hist) - 1
        
        for i in range(np.size(hist)):
                count = hist[i]
                if count > upper_threshold_pixels:
                        count = 0
                        
                found = count > lower_threshold_pixels
                
                if found:
                        hist_lower_limit = bin_edges[i]
                        break
        
        for i in range(np.size(hist) -1, -1, -1):
                count = hist[i]
                if count > upper_threshold_pixels:
                        count = 0
                
                found = count > lower_threshold_pixels
                
                if found:
                        hist_upper_limit = bin_edges[i] + bin_size
                        break
        
        if return_image:
                return window_level(arr, hist_lower_limit, hist_upper_limit)
        else:
                return hist_lower_limit, hist_upper_limit
        
        
def window_level(arr, hist_lower_limit, hist_upper_limit):
        """
        Window/level an image based on lower and upper limits
        :param arr: numpy array for the image
        :param hist_lower_limit: Lower limit of histogram
        :param hist_upper_limit: upper limit of histogram
        :return:
        """
        arr_window = arr * (arr > hist_lower_limit) * (arr < hist_upper_limit)
        arr_window = (arr_window - np.amin(arr_window)) / (np.amax(arr_window) + np.amin(arr_window))
        
        return arr_window


def overlay_arrays(array_one, array_two, intensity_threshold=0.1):
        """Plot two same-size images, with magenta/green coloring"""
        
        dims = np.shape(array_one)
        new_dims = np.zeros(len(dims)+1).astype(np.int)
        new_dims[0:len(dims)] = dims
        new_dims[len(dims)] = 3
        
        rgb_overlay = np.zeros(shape=new_dims, dtype=float)
        
        rgb_overlay[..., 0] = array_one
        rgb_overlay[..., 2] = array_one
        
        rgb_overlay[..., 1] = array_two
        
        return rgb_overlay


def bland_altman_plot(data1, data2, ylim=[-90, 90], *args, **kwargs):
        data1 = np.asarray(data1)
        data2 = np.asarray(data2)
        mean = np.mean([data1, data2], axis=0)
        diff = data1 - data2  # Difference between data1 and data2
        md = np.mean(diff)  # Mean of the difference
        sd = np.std(diff, axis=0)  # Standard deviation of the difference
        
        plt.scatter(mean, diff, *args, **kwargs)
        plt.axhline(md, color='black')
        plt.axhline(md + 1.96 * sd, color='red', linestyle='--')
        plt.axhline(md - 1.96 * sd, color='red', linestyle='--')
        plt.ylim(ylim)
        plt.ylabel('Difference')
        plt.xlabel('Mean')
