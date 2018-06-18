from pathlib import Path
import mp_img_manip.curve_align as ca
import mp_img_manip.dir_dictionary as dird
import datetime

date = str(datetime.date.today())

dir_dict = dird.create_dictionary()

def compile_results(dir_dict):
    ca.scrape_results(dir_dict['curve'], 'SHG', 'SHG_' + date)
    ca.scrape_results(dir_dict['curve'], 'MLR', 'MLR_' + date)
    ca.scrape_results(dir_dict['curve'], 'MHR', 'MHR_' + date)
    ca.scrape_results(dir_dict['curve'], 'PS', 'PS_' + date)

def analyze_results(dir_dict):
    dataframe