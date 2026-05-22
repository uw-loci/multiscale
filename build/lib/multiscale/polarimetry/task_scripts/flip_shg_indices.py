from pathlib import Path
import pandas as pd
import re


def flip_index(idx_str):
        idx = re.findall(r'\d+', idx_str)
        idx_flipped = 'ROI' + idx[1] + 'x' + idx[0] + 'y'
        return idx_flipped


path_shg = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs.csv')
df_rois = pd.read_csv(path_shg, header=[0, 1], index_col=[0, 1, 2, 3], low_memory=False)
df_shg = df_rois.xs('SHG', level=1, axis=1)
