import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats


def recast_max_diff(row):
    """Limit differences in orientation to < 90 degrees, from 180 range
    
    Input: A pandas row containing two columns.
    Output: Difference between the columns, maximum of 90 degrees
    """
    value_one, value_two = row.values
    diff = value_one - value_two
    if diff > 90:
        diff = 180 - diff
    elif diff < -90:
        diff = -180 - diff

    return diff


def recast_max_diff_90deg(row):
    value_one, value_two = row.values
    diff = value_one - value_two
    if diff > 90:
        newvalue_one = 180-value_one
        newvalue_two = value_two
    elif diff < -90:
        newvalue_two = 180 - value_two
        newvalue_one = value_one
    else:
        newvalue_one = value_one
        newvalue_two = value_two


    return newvalue_one, newvalue_two


def regress(two_column_df):
    original_columns = two_column_df.columns.tolist()
    x = two_column_df[original_columns[1]]
    y = two_column_df[original_columns[0]]

    results = stats.linregress(x, y)

    return results



def find_correlations_two_modalities(two_mod_df):
    
    recast = two_mod_df.apply(recast_max_diff_90deg, axis=1)
    group = recast.groupby(['Mouse', 'Slide']) 
    
    correlations = group.corr().iloc[0::2, 1]
    correlations.index = correlations.index.droplevel(level=2)
    
    return correlations
    