import mp_img_manip.curve_align as ca
import mp_img_manip.dir_dictionary as dird
import mp_img_manip.utility_functions as util
import mp_img_manip.cytospectre as cyto

from functools import reduce
import pandas as pd
from pathlib import Path

dir_dict = dird.create_dictionary()


def compile_results(dir_dict):
    ca.scrape_results(dir_dict['curve'], 'SHG', 'SHG_' + date)
#    ca.scrape_results(dir_dict['curve'], 'MLR', 'MLR_' + date)
#    ca.scrape_results(dir_dict['curve'], 'MHR', 'MHR_' + date)
#    ca.scrape_results(dir_dict['curve'], 'PS', 'PS_' + date)


def clean_curve_align_results(dir_dict):
    
    csv_list = util.list_filetype_in_dir(dir_dict['curve'], 'csv')
    df_list = [pd.read_csv(csv) for csv in csv_list]
    clean_list = [pd.pivot_table(flat_frame, index=['Mouse', 'Slide', 'Tile','ROI'],
                                 values=['Alignment', 'Orientation'],
                                 columns = 'Modality') for flat_frame in df_list]
    
    
    clean_df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), clean_list)
    
    tile_df = clean_df.xs('Full-tile', level='ROI')
    roi_df = clean_df.drop('Full-tile', level=2)
    
    return tile_df, roi_df
    

def clean_cytospectre_results(dir_dict):
    xls_list = util.list_filetype_in_dir(dir_dict['cyto'], 'xls')

    dirty_df_list = [pd.read_excel(xls_file, index_col='Image') for xls_file in xls_list] 
    
    clean_df_list = [cyto.clean_single_dataframe(dirty_df) for dirty_df in dirty_df_list]
    
    clean_df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), clean_df_list)
    
    return clean_df


# Sample workflow.  Take care, compile_results takes a long time and if run twice on the same date
    # Will duplicate results.

#compile_results(dir_dict)
tile_df, roi_df = clean_curve_align_results(dir_dict)
cyto_df = clean_cytospectre_results(dir_dict)

tile_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_Tiles.csv')
roi_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Curve-Align_ROIs.csv')
cyto_path = Path('F:\Box Sync\Research\Polarimetry\Data 04 - Analysis results and graphics', 'Cytospectre_Tiles.csv')

tile_df.to_csv(tile_path)
roi_df.to_csv(roi_path)
cyto_df.to_csv(cyto_path)