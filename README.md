[![Build Status](https://travis-ci.org/uw-loci/multiscale.svg?branch=master)](https://travis-ci.org/uw-loci/multiscale)

Multiscale imaging at LOCI
===================

This library holds tools for multiscale imaging projects at the Laboratory of Optical and Computational Instrumentation.
It holds tools for image registration, for interfacing with several toolkits (e.g. CurveAlign), and other processing
tasks based on project.

![Image registration demo](demo/Animation.gif)

## Submodules

This project includes several submodules.  Most submodules includes a "task_scripts" sub-submodule 
with scripts written for specific image analysis pipelines at LOCI

Some modules have a "tests" sub-folder with unit tests.
    
    ○ Imagej: Modules for working with PyImageJ.
        § Bigdata: not-yet-implemented module for converting image data into the big data viewer HDF5 and XML formats
        § Stitching: Implements BigStitcher plugin in Python
    ○ ITK: Module for working with the SimpleITK toolkit for image registration, segmentation, and analysis.
        § Itk_plotting: Methods for plotting in-progress registrations, overlay images, multiple 2d or 3d images in 
            Jupyter notebooks, and for manual selection of data points in Jupyter notebooks.
        § metadata:  Methods for reading and handling image registration and image metadata, as ITK does not work well 
            with the ImageJ file formats.  Some deprecation due to using tifffile as a writer in other locations.
        § process: Module for applying various ITK analysis functions such as windowing, applying a mask, converting to 
            8bit, and thresholding.  
        § registration: Classes for handling and plotting image registration 
        § transform: Functions for dealing with image transforms, such as from registration or scaling.
    ○ LINK_system: Module for dealing with problems specific to the LINK imaging system and related methods.
        § Coordiantes: This module contains functions for mapping between the different image coordinate transforms, 
            including opening images and doing the fiducial registration.
        § Image_classes: Module for converting between image types.  E.g., converting OCT .mat files to tifs or 
            SimpleITK images to ImageJ style images.
    ○ Microscopy: General purpose microscopy functions
        § ome: Functions for reading OME metadata 
    ○ Polarimetry: Functions that are specific to the polarimetry project 
        § Analysis: Statistical functions like finding the circular correlation coefficient on a dataframe.
        § Preprocessing: Functions for taking polarimetry data and making it usable for analysis.  E.g., taking the 24 
            polarization state images and registering them together.
        § Retardance: Functions for dealing with the retardance variable, such as how to average it by including in 
            angle information.
    ○ Toolkits: Functions that deal with specific software
        § Curve_align: Functions that specify curve align and CTFire details, such as writing ROIs or preparing for 
            CHTC bulk analysis.
        § Cw_ssim: Functions for calculating the structural-similarity coefficient
        § Cytospectre: Functions for preparing data for Cytospectre analysis
    ○ Ultrasound: Various modules related to the Verasonics ultrasound data and system used by VerasonicsScripts repostiory.
        § Beamform: incomplete/in-progress attempt at performing custom beamforming that is out-of-date.
        § Correlation: Ways to calculate the speckle autocorrelation for US images, which is a way of determining the 
            resolution. 
        § Reconstruction: Functions to take ultrasound .mat files and convert them to tifs, read the data, and process 
            it.
    ○ Bulk_img_processing: Methods to allow bulk application of functions onto files.  E.g., to find images with 
        matching "base" ([base]_[other].tif) names in two different folders for automatic registration.
    ○ Plotting: General functions for plotting used by other modules
    ○ Statistics: Statistical functions
    ○ Tiling: Functions for turning large images into smaller sub-image tiles and regions of interest.  This is helpful 
        for CHTC analysis and any other application where you want to analyze smaller regions of the interest.
    ○ Utility_functions: General functions that are used by various modules which don't quite fit in anywhere.
