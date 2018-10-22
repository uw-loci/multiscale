# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 15:42:22 2018

@author: mpinkert
"""

import multiscale.bulk_img_processing as blk
import pandas as pd
import numpy as np
from pathlib import Path


def parse_index(index_str):
        """Parse an image name of the format sample_modality_threshold_roi.ext
        
        Input:
        index_str -- A filename to parse
        
        Outputs:
        sample -- The core name/sample name
        modality -- The modality used to image the sample
        thresholds -- The intensity/number thresholds used to qualify the sample
        roi -- The individual image file/roi name
        """
        sample, modality, thresholds, roi = blk.file_name_parts(index_str)
        return sample, modality, thresholds, roi


def bulk_parse_index(index_list):
        """Parse a list of images in the format sample_modality_threshold_roi.ext
        
        Input:
        index_list -- A list containing the filenames to parse
        
        Outputs:
        parsed indices -- A list containing the following items
        [0] sample -- The core name/sample name
        [1] modality -- The modality used to image the sample
        [2] thresholds -- The thresholds used to qualify for analysis
        [3] roi -- The individual image file/roi name
        """
        
        indices_list = blk.file_name_parts_list(index_list)
        parsed_indices = np.array(indices_list)
        return parsed_indices


def parsed_indices_to_pd_index(parsed_indices):
        """ Take a list of parsed indices and turn them into a pandas multi-index
        """
        
        pre_variable_sort_index = ['Sample', 'Modality', 'Tile']
        transposed_indices = np.transpose(parsed_indices)
        clean_index_stacked = pd.MultiIndex.from_arrays(transposed_indices,
                                                        names=pre_variable_sort_index)
        
        return clean_index_stacked


def clean_single_dataframe(dirty_frame):
        """Takes a raw cytospectre dataframe and resorts it for easy analysis
        
        Input:
        dirty_frame -- A pandas dataframe of a cytospectre results file
        
        Output:
        clean_frame -- dirty_frame parsed to index by sample, thresholds, and roi,
        and with orientation/alignment columns corresponding to each modality
        """
        
        new_label_dict = {'Mean orientation': 'Orientation',
                          'Circ. variance': 'Alignment'}
        relabeled_frame = dirty_frame.rename(columns=new_label_dict)
        cutdown_frame = relabeled_frame[['Orientation', 'Alignment']]
        
        parsed_indices = bulk_parse_index(list(cutdown_frame.index))
        cluttered_index = parsed_indices_to_pd_index(parsed_indices)
        cluttered_frame = cutdown_frame.set_index(cluttered_index)
        flat_frame = cluttered_frame.reset_index()
        flat_frame[['Mouse', 'Slide']] = flat_frame['Sample'].str.split('-', expand=True)
        
        clean_frame = pd.pivot_table(flat_frame, index=['Mouse', 'Slide', 'Tile'],
                                     values=['Alignment', 'Orientation'],
                                     columns='Modality')
        
        # clean_frame = clean_frame_stacked.unstack(1)
        clean_frame['Alignment'] = clean_frame['Alignment'].apply(lambda x: 1 - x)
        
        return clean_frame


def clean_multiple_dataframes(analysis_list, output_dir, output_suffix):
        dirty_index = 'Image'
        relevant_cols = ['Mean orientation', 'Circ. variance']
        dirty_dataframes = blk.dataframe_generator_excel(analysis_list,
                                                         dirty_index,
                                                         relevant_cols)
        
        for dirty_frame in dirty_dataframes:
                clean_dataframe = clean_single_dataframe(dirty_frame)
                output_path = Path(output_dir, output_suffix)
                
                clean_dataframe.to_csv(output_path)
