# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 10:19:59 2018

@author: mpinkert
"""

import multiscale.bulk_img_processing as blk
import multiscale.tiling as til
import multiscale.utility_functions as util

import SimpleITK as sitk
import os
import numpy as np
import pandas as pd
import scipy.io as sio
from pathlib import Path
import datetime
import tarfile
import csv


def create_rois_from_tile(tile, roi_size):
        """ Create curve align rois in the matlab format for an image tile
        Input:
        tile -- A numpy array of values corresponding to the tile
        roi_size -- the size that the rois will be
        
        Output:
        separate_rois -- dictionary containing ca formatted variables
        """
        date = str(datetime.date.today())
        t = datetime.datetime.now()
        time = str(t.hour) + ':' + str(t.minute) + ':' + str(t.second)
        roi_shape = 1
        
        tile_dim = np.shape(tile)
        
        num_rois, roi_offset = til.calculate_number_of_tiles(tile_dim, roi_size, roi_size)
        
        separate_rois = {}
        
        for start, end, roi_number in til.generate_tile_start_end_index(num_rois, roi_size,
                                                                        roi_offset):
                start = start + 1
                end = end + 1
                
                roi_def = [start[0], start[1], roi_size[0], roi_size[1]]
                enclosing_rect = [start[0], start[1], end[0], end[1]]
                ym = start[1] + roi_size[1] / 2
                xm = start[0] + roi_size[0] / 2
                boundary = np.array((1,), dtype=np.object)
                boundary_object = np.array([
                        [start[1], start[0]],
                        [start[1], end[0]],
                        [end[1], end[0]],
                        [end[1], start[0]],
                        [start[1], start[0]]])
                boundary[0] = boundary_object
                
                roi = {
                        'date': date,
                        'time': time,
                        'shape': roi_shape,
                        'roi': roi_def,
                        'enclosing_rect': enclosing_rect,
                        'ym': ym,
                        'xm': xm,
                        'boundary': boundary
                }
                
                roi_name = 'ROI' + str(roi_number[0]) + 'x' + str(roi_number[1]) + 'y'
                
                separate_rois[roi_name] = roi
        
        return separate_rois


def save_rois(image_path, output_dir, output_suffix, tile_number, separate_rois,
              skip_existing_images=True):
        """ Save curve align rois as a .mat file for the curve align program
        
        Inputs:
        image_path -- Path to the base image
        output_dir -- directory where the tiles are saved
        output_suffix -- naming convention for the rois
        tile_numer -- Numerical index for the tile image
        separate_rois -- the roi dictionary
        """
        roi_suffix = output_suffix + '_' + str(tile_number[0]) + 'x-' + str(tile_number[1]) + 'y' \
                     + '_ROIs'
        
        roi_dir = Path(output_dir, 'ROI_management')
        os.makedirs(roi_dir, exist_ok=True)
        
        rois_path = blk.create_new_image_path(image_path, roi_dir, roi_suffix, extension='.mat')
        
        if rois_path.exists() and skip_existing_images:
                return
        
        sio.savemat(str(rois_path), separate_rois)


def process_image_to_rois(image_path, output_dir, output_suffix='Tile',
                          tile_size=np.array([512, 512]), tile_separation=np.array([512, 512]),
                          roi_size=np.array([64, 64]),
                          intensity_threshold=1, number_threshold=10,
                          skip_existing_images=True):
        """
        Separate a large stitched image into curve align tiles and ROIs, thresohlding out blank tiles

        :param image_path: pathlib Path to the iamge file
        :param output_dir: pathlib Path to the output diretory
        :param output_suffix: str name convention to name the output tiles
        :param tile_size: 2d numpy array of tile size.  E.g., [512, 512]
        :param tile_separation: 2d numpy array of distance between tiles.
        :param roi_size: Size of the CurveAlign ROI to process
        :param intensity_threshold: The pixel value above which pixels are conisdered signal
        :param number_threshold: Percentage of pixels above the threshold needed to write out the tile
        :param skip_existing_images: Whether or not to overwrite existing outputs

        :return:
        """
        image = sitk.ReadImage(str(image_path))
        image_array = sitk.GetArrayFromImage(image)
        max_value = np.max(image_array)
        
        for tile, tile_number in til.generate_tile(image_array, tile_size, tile_separation=tile_separation):
                
                if til.tile_passes_threshold(tile, intensity_threshold, number_threshold, max_value):
                        separate_rois = {'separate_rois': create_rois_from_tile(tile, roi_size)}
                        save_rois(image_path, output_dir, output_suffix,
                                  tile_number, separate_rois,
                                  skip_existing_images=skip_existing_images)
                        
                        til.write_tile(tile, image_path, output_dir, output_suffix,
                                       tile_number[0], tile_number[1],
                                       skip_existing_images=skip_existing_images)


def construct_job_file(tile_list, job_path):
        """
        Construct a CurveAlign job list for the CHTC batch processing software
        :param tile_list: List of image files
        :param job_path: Path to save the job file at
        :return:
        """
        with tarfile.open(job_path, 'w') as tar:
                roi_dir = tarfile.TarInfo('ROI_management')
                roi_dir.type = tarfile.DIRTYPE
                roi_dir.mode = 0o777
                
                for tile in tile_list:
                        tar.add(tile, arcname=tile.name, recursive=False)
                        roi_path = Path(tile.parent, 'ROI_management', tile.stem + '_ROIs.mat')
                        tar_roi_name = Path('ROI_management', roi_path.name)
                        tar.add(roi_path, arcname=tar_roi_name, recursive=False)


def process_folder_to_jobs(image_path, tile_dir, output_dir, output_suffix,
                           batch_size,
                           skip_existing_images=True):
        """
        Find all image tiles in a folder and process them into jobs for CHTC curve align analysis
        :param image_path: Path to the base image file that was used to create the tiles
        :param tile_dir: Directory that holds the corresponding tif tiles
        :param output_dir: Directory to output the jobs too
        :param output_suffix: Suffix string to name the jobs
        :param batch_size: How many images per job.
        :param skip_existing_images: Boolean hether to overwrite existing jobs
        :return:
        """
        tile_list = util.list_filetype_in_dir(tile_dir, '.tif')
        lists_of_job_items = util.split_list_into_sublists(tile_list, batch_size)
        list_suffix = output_suffix + '_JobList'
        
        job_list_path = blk.create_new_image_path(image_path, output_dir, list_suffix, extension='.csv')
        job_number = 1
        
        os.makedirs(output_dir, exist_ok=True)
        job_list = open(job_list_path, 'w')
        
        for tile_list in lists_of_job_items:
                job_suffix = output_suffix + '_Job-' + str(job_number)
                job_path = blk.create_new_image_path(image_path, output_dir, job_suffix, extension='.tar')
                job_number += 1
                
                if job_path.exists() and skip_existing_images:
                        continue
                
                construct_job_file(tile_list, job_path)
                job_list.write(job_path.name + '\n')


def create_batches_for_chtc(input_dir, output_dir, output_suffix,
                            tile_size=np.array([512, 512]), tile_separation=np.array([512, 512]),
                            roi_size=np.array([64, 64]),
                            intensity_threshold=1,
                            number_threshold=10,
                            batch_size=10,
                            skip_existing_images=True):
        """
        Process all image files in a folder and turn them into CHTC jobs for CurveAlign analysis
        :param input_dir:
        :param output_dir: Directory to save the output files to
        :param output_suffix: String suffix to save the files on, for (Sample)_(Suffix) format
        :param tile_size: Size of the tile in pixels.  2 element numpy array
        :param tile_separation: How distant the tiles should be for each other.  No overlap is same value as tile_size
        :param roi_size: Size of the roi in pixels
        :param intensity_threshold: What percentage of intensity is the threshold for screening out blank tiles
        :param number_threshold: Percentage of pixels in a tile that must be above the intensity threshold to be saved
        :param batch_size: How many images should be in each job
        :param skip_existing_images: Boolean whether to overwrite existing tiles or not
        :return:
        """
        
        image_path_list = util.list_filetype_in_subdirs(input_dir, '.tif')
        
        for path in image_path_list:
                tile_dir = Path(output_dir, blk.get_core_file_name(path))
                if tile_dir.exists() and skip_existing_images:
                        continue
                
                print('Tiling {0} for CHTC and Cytospectre analysis'.format(path.name))
                
                os.makedirs(tile_dir, exist_ok=True)
                
                process_image_to_rois(path, tile_dir, output_suffix=output_suffix,
                                      tile_size=tile_size, tile_separation=tile_separation,
                                      roi_size=roi_size,
                                      intensity_threshold=intensity_threshold, number_threshold=number_threshold,
                                      skip_existing_images=skip_existing_images)
                
                batch_dir = Path(tile_dir, 'Batches')
                
                process_folder_to_jobs(path, tile_dir, batch_dir, output_suffix,
                                       batch_size,
                                       skip_existing_images)
        
        return


def read_stats_file(stats_file):
        dirty_df = pd.read_csv(stats_file, delimiter='\t', header=None)
        orientation = dirty_df[1].loc[0]
        alignment = dirty_df[1].loc[4]
        
        return orientation, alignment


def extract_tar(tar_path: Path, output_dir: Path):
        """
        Extract CTFire and CurveAlign output from a tar and write it to an output folder
        :param tar_path: Path to the tar file
        :param output_dir: Path to the output directory
        :return:
        """
        with tarfile.open(tar_path) as tar:
                ca_roi = [tarinfo for tarinfo in tar.getmembers()
                          if tarinfo.name.startswith("images/CA_ROI/")]
                ca_out = [tarinfo for tarinfo in tar.getmembers()
                          if tarinfo.name.startswith("images/CA_Out/")]
                ct_fire = [tarinfo for tarinfo in tar.getmembers()
                           if tarinfo.name.startswith("images/ctFIREout/")]
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, members=ca_roi, path=output_dir)
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, members=ca_out, path=output_dir)
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, members=ct_fire, path=output_dir)


def bulk_extract_tar(tar_dir: Path, output_dir: Path):
        """
        Extract CurveAlign and CTFire output from all tars in a folder and write them to an output folder
        :param tar_dir: Path to the directory holding the tars
        :param output_dir: Path to the directory to write the output to
        :return:
        """
        tar_list = util.list_filetype_in_dir(tar_dir, 'tar')
        for tar in tar_list:
                extract_tar(tar, output_dir)
                os.remove(tar)


def scrape_tiles(tile_dir, tile_output_dir, output_suffix):
        """
        Convert a mass of CurveAlign tile output into a single file holding
        :param tile_dir:
        :param tile_output_dir:
        :param output_suffix:
        :return:
        """
        tile_files = util.list_filetype_in_dir(tile_dir, 'stats.csv')
        csv_path = Path(tile_output_dir, 'Curve_Align_results_Tiles_' + output_suffix + '.csv')
        print('Scraping results from {0}'.format(tile_dir))
        
        with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Sample', 'Modality', 'Tile', 'Orientation', 'Alignment'])
                
                for tile_path in tile_files:
                        sample, modality, tile = blk.file_name_parts(tile_path)[:3]
                        orientation, alignment = read_stats_file(tile_path)
                        if 'NaN' in str(alignment):
                                continue
                                
                        writer.writerow([sample, modality, tile, orientation, alignment])


def scrape_rois(roi_dir, roi_output_dir, output_suffix):
        roi_files = util.list_filetype_in_dir(roi_dir, 'stats.csv')
        csv_path = Path(roi_output_dir, 'Curve_Align_results_ROIs_' + output_suffix + '.csv')
        print('Scraping results from {0}'.format(roi_dir))
        
        with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Sample', 'Modality', 'Tile', 'ROI', 'Orientation', 'Alignment'])
                
                for roi_path in roi_files:
                        sample, modality, tile, roi = blk.file_name_parts(roi_path)[:4]
                        orientation, alignment = read_stats_file(roi_path)
                        if 'NaN' in str(alignment):
                                continue
                                
                        writer.writerow([sample, modality, tile, roi, orientation, alignment])


def read_features_file(file_path):
        try:
                df_features = pd.read_csv(file_path, header=None)
        except ValueError:
                return np.nan, np.nan
        
        unique = df_features.nunique()
        num_fibers = unique[0]
        fib_segments = df_features.shape[0]
        
        return num_fibers, fib_segments


def scrape_roi_fiber_nums(roi_dir, roi_output_dir, output_suffix):
        roi_files = util.list_filetype_in_dir(roi_dir, 'fibFeatures.csv')
        csv_path = Path(roi_output_dir, 'Curve_Align_results_ROIs_' + output_suffix + '.csv')
        print('Scraping results from {0}'.format(roi_dir))
        
        with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Sample', 'Modality', 'Tile', 'ROI', 'Number of fibers', 'Fiber segments'])
                
                for roi_path in roi_files:
                        sample, modality, tile, roi = blk.file_name_parts(roi_path)[:4]
                        num_fibers, fib_segments = read_features_file(roi_path)
                        if num_fibers is np.nan:
                                continue
                        
                        writer.writerow([sample, modality, tile, roi, num_fibers, fib_segments])


def scrape_features(curve_dir, modality_str, output_suffix):
        roi_dir = Path(curve_dir, modality_str + '\images\CA_ROI\Batch\ROI_post_analysis')
        roi_output_dir = Path(curve_dir, 'ROI')
        os.makedirs(roi_output_dir, exist_ok=True)
        scrape_roi_fiber_nums(roi_dir, roi_output_dir, output_suffix)


def scrape_results(curve_dir, modality_str, output_suffix):
        """
        Convert CurveAlign ROI and Tile analysis files into a single csv document for orientation and alignment
        :param curve_dir: Directory where the CurveAlign output was printed to
        :param modality_str: What modality was used to take the data, in format (Sample-name_Modality_...tif)
        :param output_suffix: What to label the output csv file
        :return:
        """
        tile_dir = Path(curve_dir, r'images\CA_Out')
        if tile_dir.exists():
                tile_output_dir = Path(curve_dir, 'Tile')
                os.makedirs(tile_output_dir, exist_ok=True)
                scrape_tiles(tile_dir, tile_output_dir, output_suffix)
                print('Done')
        
        roi_dir = Path(curve_dir, r'images\CA_ROI\Batch\ROI_post_analysis')
        print(roi_dir.exists())
        if not roi_dir.exists():
                print('Somehow got here anyway')
                roi_dir = Path(curve_dir, r'images\CA_ROI\Batch\CA_Out')
                
        roi_output_dir = Path(curve_dir, 'ROI')
        os.makedirs(roi_output_dir, exist_ok=True)
        scrape_rois(roi_dir, roi_output_dir, output_suffix)


def load_dataframe(csv_path):
        raw_df = pd.read_csv(csv_path)
        
        clean_df = pd.pivot_table(raw_df, index=['Sample', 'Tile', 'ROI'],
                                  values=['Alignment', 'Orientation'],
                                  columns='Modality')
        
        return clean_df
