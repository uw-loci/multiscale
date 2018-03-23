import os
import mp_img_manip.utility_functions as util
import pandas as pd

    
def read_write_pandas_row(file_path, index,
                          index_label, column_labels,
                          column_values = None):
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
    
    #todo: make it query based on the type, and not just a str
    
    (file_dir, file_name) = os.path.split(file_path)
    try:
        data = pd.read_csv(file_path, index_col = index_label)
        if (data.index == index).any():
            if column_values:
                print('Row values in ' + file_name + ':')
                print('\t' + data.loc[index])
                
                print('User entered row values:')
                print('\t' + str(column_values))
                
                if not util.yes_no(
                        'Do you want to replace the file values with your '
                        'newly entered values'):
                    column_values = data.loc[index]
                    
            else: column_values = data.loc[index]            
    except:
        print('\n Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(
                index = pd.Index([], dtype='object', name=index_label),
                columns = column_labels)
            
    if column_values is not None:
        data.loc[index] = column_values
    else:
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
    
    (file_dir, file_name) = os.path.split(file_path)
    
    try:
        data = pd.read_csv(file_path, index_col = index_label)
        return data.loc[index]
    except:
        print('The file does not exist')
        return []
    

def write_pandas_value(file_path, index, value, 
                       index_label, column, column_labels):
    
    (file_dir, file_name) = os.path.split(file_path)
    
    try:
        data = pd.read_csv(file_path, index_col = index_label)
    except: 
        print('Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(
                index = pd.Index([], dtype='object', name=index_label),
                columns = column_labels)
        
    data.loc[column, index_label] = value
    data.to_csv(file_path)
    

def file_name_parts(file_name):
    """Extract strings seperated by underscores in a file name"""
    full_file_name = os.path.split(file_name)[1]
    
    name_str = os.path.splitext(full_file_name)[0]
    
    underscore_indices = util.character_indices(name_str, '_')
    
    if underscore_indices[0] == -1:
        print('The file name ' + name_str + ' has only one part.')
        return name_str
    
    underscore_indices.append(len(name_str))
    
    part_list = []
    part_list.append(name_str[:int(underscore_indices[0])])
     
    for i in range(1,len(underscore_indices)):
        
        part_list.append(
                name_str[(underscore_indices[i-1]+1):underscore_indices[i]])
    
    return part_list
    


def get_core_file_name(file_name):
    """This function extracts the file string up until the first underscore"""
    
    full_file_name = os.path.split(file_name)[1]
    
    name_str = os.path.splitext(full_file_name)[0]
    
    underscore_index = name_str.find('_')
    
    if underscore_index > 0:     
        return name_str[0:underscore_index]
    else:
        return name_str
    
	
def create_new_image_path(core_image_path, output_dir, output_suffix):
    """Create a new path for an image that has been modified
    
    Inputs:
    core_image_path -- The path to the original image
    output_dir -- The directory for the new image
    output_suffix -- How the new file is named in text
    
    Output:
    new_path -- A path for the new image
    """
    
    core_name = get_core_file_name(core_image_path)
    
    new_name = core_name + '_' + output_suffix + '.tif'
        
    new_path = os.path.join(output_dir, new_name)
    return new_path
    

def find_shared_images(dir_one, dir_two):
    """images from two directories are paired based on base names
    
    Input:
    dir_one -- Directory for the first set of images
    dir_two -- Directory for the second set of images.
    
    Outputs:
    Two lists, where same index corresponds to paired images
    """
    
    #todo: modify dir_one_baseFile_names into a list of names, and then
    #implement a .txt file?
    
    #todo: make a check for different categories of name,
    #   if there are multiple instances of a single name?
    
    file_list_one = [f for f in os.listdir(dir_one) if f.endswith('.tif')]
    file_list_two = [f for f in os.listdir(dir_two) if f.endswith('.tif')]
        
    dir_one_image_paths = list()
    dir_two_image_paths = list()

    for i in range(0,len(file_list_one)):
        core_nameOne = get_core_file_name(file_list_one[i])
        
        for j  in range(0,len(file_list_two)):
            core_nameTwo = get_core_file_name(file_list_two[j])
          
            if core_nameOne == core_nameTwo:
                
                dir_one_image_paths.append(
                        os.path.join(dir_one, file_list_one[i]))
                dir_two_image_paths.append(
                        os.path.join(dir_two, file_list_two[j]))

    
    return (dir_one_image_paths, dir_two_image_paths)