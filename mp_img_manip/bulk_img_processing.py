import os
import mp_img_manip.utility_functions as util
import pandas as pd
from pathlib import Path


def dataframe_generator_excel(analysis_list, index, relevant_cols=None):
        """
        Generator to yield dataframes from a list of excel docs, one at a time
        
        analysis_list = the list of excel docs
        index = index column of the excel doc
        relevant_cols = subset of dataframe to return
        """
        
        if relevant_cols is None:
                for item in analysis_list:
                        dataframe = pd.read_excel(str(item), index_col = index)
                        dataframe.name = item.stem
                        yield dataframe
        else:
                for item in analysis_list:
                        df = pd.read_excel(str(item), index_col = index)
                        output_df = df[relevant_cols]
                        output_df.name = item.stem
                        yield output_df


def dataframe_generator_csv(analysis_list):
        """
        Generator to yield dataframes from a list of excel docs, one at a time
        
        analysis_list = the list of excel docs
        index = index column of the excel doc
        relevant_cols = subset of dataframe to return
        """
        for item in analysis_list:
                df = pd.read_csv(str(item))
                yield df


def read_write_pandas_row(file_path, index,
                          index_label, column_labels):
        """
        Read a row from a csv file, or create it if it does not exist.
        
        Inputs:
        file_path -- path and name of csv file
        index -- the specific index you are looking for
        index_label -- what is the first entry of the index column
        column_labels -- labels for each column/variable
        column_values -- optional manual user input of values
        
        Output:
        The csv row in a list, absent the index.
        """
        
        # todo: make it query based on the type, and not just a str
        
        (file_dir, file_name) = os.path.split(file_path)
        try:
                data = pd.read_csv(file_path, index_col = index_label)
        except:
                print('\n Creating new file ' + file_name + ' in ' + file_dir)
                data = pd.DataFrame(
                        index=pd.Index([], dtype='object', name=index_label),
                        columns=column_labels)
        
        try:
                return data.loc[index]
        except:
                print('Please enter in values for {0}'.format(index))
                new_row = [input(x + ': ') for x in column_labels]
                data.loc[index] = new_row
                
                data.to_csv(file_path)
                return data.loc[index]


def write_pandas_row(file_path, index, column_values,
                     index_label, column_labels):
        """Write a new row to a .csv file, or create it does not exist
        
        Inputs:
        file_path -- path and name of csv file
        index -- the specific index you are looking for
        column_values -- the values for each variable
        index_label -- what is the first entry of the index column
        column_labels -- labels for each column/variable
        """
        (file_dir, file_name) = os.path.split(file_path)
        
        try:
                data = pd.read_csv(file_path, index_col = index_label)
        except:
                print('Creating new file ' + file_name + ' in ' + file_dir)
                data = pd.DataFrame(
                        index = pd.Index([], dtype='object', name=index_label),
                        columns = column_labels)
        
        data.loc[index] = column_values
        data.to_csv(file_path)


def read_pandas_row(file_path, index, index_label):
        """Read a row from a .csv file"""
        
        try:
                data = pd.read_csv(file_path, index_col=index_label)
                return data.loc[index]
        except:
                print('The file does not exist')
                return []


def write_pandas_value(file_path, index, value, column,
                       index_label):
        
        (file_dir, file_name) = os.path.split(file_path)
        
        try:
                data = pd.read_csv(file_path, index_col = index_label)
        except:
                print('Creating new file ' + file_name + ' in ' + file_dir)
                data = pd.DataFrame(
                        index = pd.Index([], dtype='object', name=index_label))
        
        data.loc[index, column] = value
        data.to_csv(file_path)


def file_name_parts(file_name):
        """Extract strings seperated by underscores in a file name"""
        
        name_str = Path(file_name).stem
        
        part_list = str(name_str).split('_')
        
        return part_list


def file_name_parts_list(file_list):
        """Extract underscore separated parts in a list of file names"""
        parts_list = [file_name_parts(file_name) for file_name in file_list]
        return parts_list


def get_core_file_name(file_name):
        """This function extracts the file string up until the first underscore"""
        
        name_str = Path(file_name).stem
        part_list = str(name_str).split('_')
        
        return part_list[0]


def create_new_image_path(core_image_path, output_dir, output_suffix=None,
                          extension='.tif'):
        """Create a new path for an image that has been modified
        
        Inputs:
        core_image_path -- The path to the original image
        output_dir -- The directory for the new image
        output_suffix -- How the new file is named in text
        
        Output:
        new_path -- A path for the new image
        """
        
        core_name = get_core_file_name(core_image_path)
        
        if output_suffix is not None:
                new_name = core_name + '_' + output_suffix + extension
        else:
                new_name = core_name + extension
        
        new_path = Path(output_dir, new_name)
        return new_path


def find_shared_images(dir_one, dir_two):
        """images from two directories are paired based on base names
        
        Input:
        dir_one -- Directory for the first set of images
        dir_two -- Directory for the second set of images.
        
        Outputs:
        Two lists, where same index corresponds to paired images
        """
        # todo: make a check for different categories of name,
        #   if there are multiple instances of a single name?
        
        file_list_one = [Path(f) for f in os.listdir(dir_one) if f.endswith('.tif')]
        file_list_two = [Path(f) for f in os.listdir(dir_two) if f.endswith('.tif')]
        
        dir_one_image_paths = list()
        dir_two_image_paths = list()
        
        for i in range(0,len(file_list_one)):
                core_name_one = get_core_file_name(file_list_one[i])
                
                for j  in range(0,len(file_list_two)):
                        core_name_two = get_core_file_name(file_list_two[j])
                        
                        if core_name_one == core_name_two:
                                
                                dir_one_image_paths.append(Path(dir_one, file_list_one[i]))
                                dir_two_image_paths.append(Path(dir_two, file_list_two[j]))
        
        return dir_one_image_paths, dir_two_image_paths


def core_names_in_list(path_list):
        """Return a list of the core names for each item in the path list"""
        return [get_core_file_name(item) for item in path_list]


def trim_file_parts_list(file_parts_list, parts_to_keep=[0]):
        list_trimmed = [file_parts_list[idx] for idx in parts_to_keep]
        return list_trimmed


def find_bulk_shared_images(dir_list, file_parts_to_compare=[0], subdirs=False):
        """images from two or more directories are paired based on core names
        
        Input:
        dir_list - list of the directories to be compared
        file_parts_to_compare - File part is a string separated by _, to compare is idx on parts, default first string
        subdirs - whether to look for files in subdirs of given directory or just dirs
    
        Outputs:
        A list of path lists, for corresponding images
        """
        
        num_dirs = len(dir_list)
        
        if subdirs:
                list_of_file_lists = [util.list_filetype_in_subdirs(dir_list[index], '.tif') for
                                      index in range(num_dirs)]
        else:
                list_of_file_lists = [util.list_filetype_in_dir(dir_list[index], '.tif') for
                                      index in range(num_dirs)]
        
        list_of_file_parts_lists = [file_name_parts_list(list_of_file_lists[index]) for index in range(num_dirs)]
        
        relevant_file_parts = [[trim_file_parts_list(parts_list, file_parts_to_compare)
                                for parts_list in list_of_file_parts_lists[directory]]
                               for directory in range(num_dirs)]
        
        path_lists = []
        for i in range(num_dirs):
                path_lists.append([])
        
        for item in relevant_file_parts[0]:
                if util.item_present_all_lists(item, relevant_file_parts[1:]):
                        for index in range(num_dirs):
                                item_index = relevant_file_parts[index].index(item)
                                new_path = Path(list_of_file_lists[index][item_index])
                                path_lists[index].append(new_path)
        
        return path_lists
