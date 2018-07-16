import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats


def add_diffs_column_to_dataframe(dataframe):
    return


def find_diff(two_column_df):
    recast_df = two_column_df.apply(recast_max_diff_90deg, axis = 1)
    # find diff between two columns of arbitrary name..


def recast_max_diff_90deg(row):
    value_one, value_two = row.values
    diff = value_one - value_two
    if diff > 90:
        new_value = value_one - 180.0
    elif diff < -90:
        new_value = value_one + 180.0
    else:
        new_value = value_one + 0

    return new_value, value_two


def regress(two_column_df):
    original_columns = two_column_df.columns.tolist()
    x = two_column_df[original_columns[1]]
    y = two_column_df[original_columns[0]]

    results = stats.linregress(x, y)

    return results



def find_correlations_two_modalities(two_mod_df):
    
    recast = two_mod_df.apply(recast_max_diff_90deg, axis=1)
    group = recast.groupby(['Mouse', 'Slide']) 
    
    correlations = group.corr().ix[0::2, 1]
    
    return correlations
    