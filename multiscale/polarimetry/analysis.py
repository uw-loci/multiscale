import itertools as itt

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats
import pycircstat as circ

import multiscale.statistics as mstat


def regress(two_column_df: pd.DataFrame) -> np.ndarray:
        original_columns = two_column_df.columns.tolist()
        x = two_column_df[original_columns[1]]
        y = two_column_df[original_columns[0]]
        
        results = np.array(stats.linregress(x, y))
        
        return results


def find_circular_correlations(two_mod_df: pd.DataFrame):
        df_nonan = two_mod_df.dropna()
        grouped = df_nonan.groupby(['Mouse', 'Slide'])
        correlations = {}
        mouse = []
        slide = []
        for name, group in grouped:
                radians = group.values*2*np.pi/180
                n = np.shape(radians)[0]
                if n < 100:
                        continue
                corr = circ.corrcc(radians[:, 0], radians[:, 1])
                correlations[name] = [corr, n]
                mouse.append(name[0])
                slide.append(name[1])
                
        index = pd.MultiIndex.from_arrays([mouse, slide], names=['Mouse', 'Slide'])
        correlations = pd.DataFrame.from_dict(correlations, orient='index', columns=['Correlation', 'n'])
        correlations.set_index(index, inplace=True)
        
        return correlations


def calculate_pairwise_correlations(df_variable: pd.DataFrame) -> dict:
        """For each pair of modalities, calculate correlations, and put them together into a column"""
        
        modalities = list(df_variable.columns.values)
        
        df_dict = {}
        modality_iterator = itt.combinations(modalities, 2)
        for pair in modality_iterator:
                corr_pair = find_circular_correlations(df_variable.loc[:, pair])
                header = '-'.join(pair)
                
                df_dict[header] = corr_pair
                
        return df_dict


def pairwise_Z_p(df_Z: pd.DataFrame):
        """
        Calculate the p-value for different combinations of Z values
        :param df_Z: Dataframe organized in a row as Group: Z, SE
        :return: pairwise Z series
        """
        names = list(df_Z.index)
        p_dict = {}
        name_iterator = itt.combinations(names, 2)

        for pair in name_iterator:
                z1, se1 = df_Z.loc[pair[0]]
                z2, se2 = df_Z.loc[pair[1]]
                index = '-'.join(pair)
                
                p = mstat.z_t_test(z1, se1, z2, se2)
                p_dict[index] = p
                
        return p_dict

