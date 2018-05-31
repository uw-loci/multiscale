# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 09:25:11 2018

@author: mpinkert
"""
import matplotlib.pyplot as plt
import numpy as np

def plot_colored_overlay(array_one, array_two, difference_threshold=0.1):
    """Plot two same-size images in 3 channels, with blue->same position"""
    
    diff = array_one - array_two
    abs_diff = np.abs(diff)    
    dims = np.shape(diff)
    
    grayscale = abs_diff < difference_threshold
    red = diff > 0.1
    green = diff < -0.1

    rgb_overlay = np.zeros(shape=(dims[0], dims[1], 3), dtype=float)
    
    rgb_overlay[grayscale, 2] = np.ma.masked_array(array_one[grayscale])
    rgb_overlay[red, 0] = np.ma.masked_array(array_one[red])
    rgb_overlay[green, 1] = np.ma.masked_array(array_two[green])
    
    return rgb_overlay
    

def bland_altman_plot(data1, data2, *args, **kwargs):
    data1     = np.asarray(data1)
    data2     = np.asarray(data2)
    mean      = np.mean([data1, data2], axis=0)
    diff      = data1 - data2                   # Difference between data1 and data2
    md        = np.mean(diff)                   # Mean of the difference
    sd        = np.std(diff, axis=0)            # Standard deviation of the difference

    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,           color='black')
    plt.axhline(md + 1.96*sd, color='red', linestyle='--')
    plt.axhline(md - 1.96*sd, color='red', linestyle='--')
    plt.ylim([-90, 90])
    plt.ylabel('Difference')
    plt.xlabel('Mean')
