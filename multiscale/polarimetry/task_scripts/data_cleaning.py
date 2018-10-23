import multiscale.toolkits.curve_align as ca
import multiscale.polarimetry.dir_dictionary as dird
import multiscale.utility_functions as util
import multiscale.toolkits.cytospectre as cyto

from functools import reduce
import pandas as pd
from pathlib import Path
import datetime

date = str(datetime.date.today())

dir_dict = dird.create_dictionary()


def compile_results(dir_dict):
        ca.scrape_results(dir_dict['curve'], 'SHG', 'SHG_' + date)
        ca.scrape_results(dir_dict['curve'], 'MLR', 'MLR_' + date)
        ca.scrape_results(dir_dict['curve'], 'MHR', 'MHR_' + date)


#    ca.scrape_results(dir_dict['curve'], 'PS', 'PS_' + date)


def clean_curve_align_tiles(dir_dict):
        csv_list = util.list_filetype_in_dir(Path(dir_dict['curve'], 'Tile'), 'csv')
        df_list = [pd.read_csv(csv) for csv in csv_list]
        clean_list = [pd.pivot_table(flat_frame, index=['Mouse', 'Slide', 'Tile'],
                                     values=['Alignment', 'Orientation'],
                                     columns='Modality') for flat_frame in df_list]
        
        clean_tile_df = reduce(lambda x, y: pd.concat([x, y], axis=1), clean_list)
        
        return clean_tile_df


def clean_curve_align_rois(dir_dict):
        csv_list = util.list_filetype_in_dir(Path(dir_dict['curve'], 'ROI'), 'csv')
        df_list = [pd.read_csv(csv, dtype={'Mouse': object, 'Slide': object}) for csv in csv_list]
        clean_list = [pd.pivot_table(flat_frame, index=['Mouse', 'Slide', 'Tile', 'ROI'],
                                     values=['Alignment', 'Orientation'],
                                     columns='Modality') for flat_frame in df_list]
        
        clean_roi_df = reduce(lambda x, y: pd.concat([x, y], axis=1), clean_list)
        
        return clean_roi_df


def clean_cytospectre_results(dir_dict):
        xls_list = util.list_filetype_in_dir(dir_dict['cyto'], 'xls')
        
        df_list_dirty = [pd.read_excel(xls_file, index_col='Image') for xls_file in xls_list]
        
        df_list_clean = [cyto.clean_single_dataframe(dirty_df) for dirty_df in df_list_dirty]
        
        clean_df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), df_list_clean)
        
        return clean_df


# Sample workflow.  Take care, compile_results takes a long time and if run twice on the same date
# Will duplicate results.

#compile_results(dir_dict)
df_tile = clean_curve_align_tiles(dir_dict)
df_roi = clean_curve_align_rois(dir_dict)
df_cyto = clean_cytospectre_results(dir_dict)

path_tile = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                 'Curve-Align_Tiles.csv')
path_roi = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                'Curve-Align_ROIs.csv')
path_cyto = Path('F:\Research\Polarimetry\Data 04 - Analysis results and graphics',
                 'Cytospectre_Tiles.csv')

df_tile.to_csv(path_tile)
df_roi.to_csv(path_roi)
df_cyto.to_csv(path_cyto)
