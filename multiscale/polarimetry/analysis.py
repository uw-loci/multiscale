import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats
import pycircstat as circ


def regress(two_column_df: pd.DataFrame) -> np.ndarray:
        original_columns = two_column_df.columns.tolist()
        x = two_column_df[original_columns[1]]
        y = two_column_df[original_columns[0]]
        
        results = stats.linregress(x, y)
        
        return results


def find_circular_correlations(two_mod_df: pd.DataFrame):
        grouped = two_mod_df.groupby(['Mouse', 'Slide'])
        correlations = {}
        for name, group in grouped:
                radians = group.values*2*np.pi/180
                if np.shape(radians)[0] < 100:
                        continue
                corr = circ.corrcc(radians[:, 0], radians[:, 1])
                correlations[name] = corr
        return correlations
