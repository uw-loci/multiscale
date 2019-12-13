# -*- coding: utf-8 -*-
"""
Project specific functions for processing polarimetry results into statistics

Created on Tue Jun 19 16:11:52 2018

@author: mpinkert
"""

import multiscale.polarimetry.analysis as an
import multiscale.statistics as stat
import pandas as pd
from pathlib import Path


def get_tile_roi_cyto_df(tile_path, roi_path, cyto_path):
        tile_df = pd.read_csv(tile_path, header=[0, 1], index_col=[0, 1, 2],
                              low_memory=False)
        roi_df = pd.read_csv(roi_path, header=[0, 1], index_col=[0, 1, 2, 3],
                             low_memory=False)
        cyto_df = pd.read_csv(cyto_path, header=[0, 1], index_col=[0, 1, 2],
                              low_memory=False)
        
        return tile_df, roi_df, cyto_df


def run_tile_roi_cyto():
        tile_path = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics\Old files',
                         'Curve-Align_Tiles.csv')
        roi_path = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics\Old files',
                        'Curve-Align_ROIs_18.csv')
        cyto_path = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics\Old files',
                         'Cytospectre_Tiles.csv')
        
        df_tile, df_roi, df_cyto = get_tile_roi_cyto_df(tile_path, roi_path, cyto_path)
        
        pheno_tile = calculate_corrs_by_phenotype(df_tile)
        pheno_roi = calculate_corrs_by_phenotype(df_roi)
        pheno_cyto = calculate_corrs_by_phenotype(df_cyto)
        
        return pheno_tile, pheno_roi, pheno_cyto


def calculate_corrs_by_phenotype(df_single_measure):
        corrs = an.calculate_pairwise_correlations(df_single_measure)
        pheno_corrs = group_into_phenotypes(corrs)
        return pheno_corrs


def display_corrs(pheno_corrs):
        print('Benign')
        print(pheno_corrs[0].describe()[0:3])
        
        print('Cancerous')
        print(pheno_corrs[1].describe()[0:3])
        
        print('Col1a1/Benign')
        print(pheno_corrs[2].describe()[0:3])
        
        print('Col1a1/Cancerous')
        print(pheno_corrs[3].describe()[0:3])


def group_into_phenotypes(dataframe):
        wild_benign = dataframe.loc[['WT1', '1047']]
        wild_cancer = dataframe.loc[['WP', '2944', '1046', '1367']]
        col1a1_benign = dataframe.loc[['1054', '1064']]
        col1a1_cancer = dataframe.loc[['1045', '1057', '1061']]
        
        return wild_benign, wild_cancer, col1a1_benign, col1a1_cancer


def z_and_se_phenotype(df, phenotype):
        """
        Find the Z value and the se for a phenotype
        :param df:
        :return:
        """
        corr = stat.mean_correlation(df['Correlation'])
        se = stat.z_standard_error(df['Correlation'].size)
        return corr, se


def pheno_to_z_df(wild_benign, wild_cancer, col1a1_benign, col1a1_cancer):
        wb_corr, wb_se = z_and_se_phenotype(wild_benign, 'wt/cancer')
        wc_corr, wc_se = z_and_se_phenotype(wild_cancer, 'wt/cancer')
        cb_corr, cb_se = z_and_se_phenotype(col1a1_benign, 'col1/benign')
        cc_corr, cc_se = z_and_se_phenotype(col1a1_cancer, 'col1/cancer')
        
        data = {'Wild benign': [wb_corr, wb_se], 'Wild cancer': [wc_corr, wc_se], 'Col1 benign': [cb_corr, cb_se],
                'Col1 cancer': [cc_corr, cc_se]}
        
        df_z = pd.DataFrame.from_dict(data, orient='index', columns=['Z', 'SE'])
        return df_z
        

def p_value_between_phenotypes(df_corr):
        wild_benign, wild_cancer, col1a1_benign, col1a1_cancer = group_into_phenotypes(df_corr)
        df_z = pheno_to_z_df(wild_benign, wild_cancer, col1a1_benign, col1a1_cancer)
        p_dict = an.pairwise_Z_p(df_z)
        return p_dict
        


def find_nas(single_variable_df):
        return single_variable_df.isnull().groupby(['Mouse', 'Slide']).sum().astype(int)


def threshold_df_by_retardance(df_measure, df_ret, threshold):
        df_mhr_mlr = df_measure[['MLR', 'MHR']]
        df_measure[['MLR', 'MHR']] = df_mhr_mlr[df_ret > threshold]
        return df_measure


def get_average_dfs(path_shg: Path, path_average: Path, ret_thresh: float) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        # df_rois = pd.read_csv(path_shg, header=[0, 1], index_col=[0, 1, 2, 3],
        #                      low_memory=False)
        # df_shg = df_rois.xs('SHG', level=1, axis=1)
        
        df_shg = pd.read_csv(path_shg, header=[0, 1], index_col=[0, 1, 2, 3], low_memory=False)
        
        df_average = pd.read_csv(path_average, header=[0, 1], index_col=[0, 1, 2, 3],
                                 low_memory=False)
        
        df_average.rename(index=str, columns={'MHR-O': 'MHR', 'MLR-O': 'MLR', 'PS-O': 'PS'}, inplace=True)
        
        df_ret = df_average.loc[:, 'Retardance'].copy()
        mask = df_ret > ret_thresh
        
        df_orient = df_average.loc[:, 'Orientation'].copy()
        df_orient = df_orient[mask]
        df_orient.loc[:, 'SHG'] = df_shg.loc[:, 'Orientation'].copy()
        
        df_align = df_average.loc[:, 'Alignment'].copy()
        df_align = df_align[df_ret > ret_thresh]
        df_align.loc[:, 'SHG'] = df_shg.loc[:, 'Alignment'].copy()
        
        return df_orient, df_align, df_ret


def run_roi_averages_comparison(ret_thresh: float) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        path_shg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs_new.csv')
        path_average = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                            'ROIs_averaged_from_base_image_old.csv')
        
        df_orient, df_align, df_ret = get_average_dfs(path_shg, path_average, ret_thresh)
        
        df_corrs_orient = an.calculate_pairwise_correlations(df_orient)
        df_corrs_align = an.calculate_pairwise_correlations(df_align)
        df_corrs_ret = an.calculate_pairwise_correlations(df_ret)
        
        return df_corrs_orient, df_corrs_align, df_corrs_ret


def threshold_by_fiber_num(df, fib_thresh):
        idx_threshold = df['Number of fibers'] > fib_thresh
        df_threshold = df[idx_threshold]
        df_modalities = df_threshold[['SHG', 'MLR-O', 'MHR-O', 'PS-O', 'Fiber segments']]
        
        return df_modalities


def threshold_by_fiber_segments(df, seg_thresh):
        idx_threshold = df['Fiber segments'] > seg_thresh
        df_threshold = df[idx_threshold]
        df_modalities = df_threshold[['SHG', 'MLR-O', 'MHR-O', 'PS-O']]
        
        return df_modalities


def fib_comparison(ret_thresh: float, fib_thresh: int, seg_thresh: int):
        path_shg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs.csv')
        path_average = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                            'ROIs_averaged_from_base_image.csv')
        path_fibs = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics\Curve Align',
                         'CA_FibNum_SHG.csv')
        
        df_orient, df_align, df_ret = get_average_dfs(path_shg, path_average, ret_thresh)
        df_fibs = pd.read_csv(path_fibs, index_col=[0, 1, 2, 3], low_memory=False)
        
        df_orient_merged = pd.concat([df_orient, df_fibs], axis=1, join='inner')
        df_orient_thresh_1 = threshold_by_fiber_num(df_orient_merged, fib_thresh)
        df_orient_thresh_2 = threshold_by_fiber_segments(df_orient_thresh_1, seg_thresh)
        
        df_align_merged = pd.concat([df_align, df_fibs], axis=1, join='inner')
        df_align_thresh_1 = threshold_by_fiber_num(df_align_merged, fib_thresh)
        df_align_thresh_2 = threshold_by_fiber_segments(df_align_thresh_1, seg_thresh)
        
        corrs_orient = an.calculate_pairwise_correlations(df_orient_thresh_2)
        corrs_align = an.calculate_pairwise_correlations(df_align_thresh_2)
        
        return corrs_orient, corrs_align

#
# corrs_orient, corrs_align = fib_comparison(2, 0, 0)
# print(corrs_orient)
# print(corrs_align)
#
# path_avg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
#                 'ROIs_averaged_from_base_image.csv')
# path_shg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs_new.csv')
#
# df_orient, df_align, df_ret = get_average_dfs(path_shg, path_avg, 0.1)

run_roi_averages_comparison(0.5)
print('hello')
