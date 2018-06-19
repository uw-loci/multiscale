import mp_img_manip.curve_align as ca
import mp_img_manip.dir_dictionary as dird
import mp_img_manip.utility_functions as util

from functools import reduce
import pandas as pd
import datetime

date = str(datetime.date.today())

dir_dict = dird.create_dictionary()

def compile_results(dir_dict):
    ca.scrape_results(dir_dict['curve'], 'SHG', 'SHG_' + date)
    ca.scrape_results(dir_dict['curve'], 'MLR', 'MLR_' + date)
    ca.scrape_results(dir_dict['curve'], 'MHR', 'MHR_' + date)
    ca.scrape_results(dir_dict['curve'], 'PS', 'PS_' + date)

def clean_results(dir_dict):
    
    csv_list = util.list_filetype_in_dir(dir_dict['curve'], 'csv')
    df_list = [pd.read_csv(csv) for csv in csv_list]
    clean_list = [pd.pivot_table(flat_frame, index=['Sample', 'Tile','ROI'],
                                 values=['Alignment', 'Orientation'],
                                 columns = 'Modality') for flat_frame in df_list]
    
    
    clean_df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), clean_list)
    
    tile_df = clean_df.xs('Full-tile', level='ROI')
    roi_df = clean_df.drop('Full-tile', level=2)
    
    return tile_df, roi_df
    

#compile_results(dir_dict)
tile_df, roi_df = clean_results(dir_dict)