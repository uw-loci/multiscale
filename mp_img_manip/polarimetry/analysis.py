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
        new_value_one = 180-value_one
        new_value_two = value_two
    elif diff < -90:
        new_value_two = 180 - value_two
        new_value_one = value_one
    else:
        new_value_one = value_one
        new_value_two = value_two

    return new_value_one, new_value_two


def regress(two_column_df: pd.DataFrame) -> np.ndarray:
    original_columns = two_column_df.columns.tolist()
    x = two_column_df[original_columns[1]]
    y = two_column_df[original_columns[0]]

    results = stats.linregress(x, y)

    return results


def find_correlations_two_modalities(two_mod_df: pd.DataFrame, recast: bool=False) -> pd.Series:
    if recast:
        recast = two_mod_df.apply(recast_max_diff_90deg, axis=1)
        group = recast.groupby(['Mouse', 'Slide'])
    else:
        group = two_mod_df.groupby(['Mouse', 'Slide'])

    correlations = group.corr().iloc[0::2, 1]
    correlations.index = correlations.index.droplevel(level=2)
    
    return correlations
