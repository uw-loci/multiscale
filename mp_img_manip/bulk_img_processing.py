import os
import mp_image_manip.utility_functions as util
import pandas as pd

    
def read_write_pandas_row(file_path, index,
                          index_label, column_labels):
        
    (file_dir, file_name) = os.path.split(file_path)

    try:
        data = pd.read_csv(file_path, index_col = index_label)
        try:
            return data.loc[index]
        except:
            print('There are no existing entries for ' + index )
    except:
        print('Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(
                index = pd.Index([], dtype='object', name=index_label),
                columns = column_labels)
    
    print('Please enter in values for {0}'.format(index))
    new_row = [input(x + ': ') for x in column_labels]
    data.loc[index] = new_row 
    
    data.to_csv(file_path)
        
    return data.loc[index]
        
        
def write_pandas_row(file_path, index, column_values,
                     index_label, column_labels):
        
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
        

def file_name_parts(file_name):
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
    


def get_base_file_name(file_name):
    """This function extracts the 'base name' of a file, which is defined as
    the string up until the first underscore, or until the extension if
    there is no underscore"""
    
    full_file_name = os.path.split(file_name)[1]
    
    name_str = os.path.splitext(full_file_name)[0]
    
    underscore_index = name_str.find('_')
    
    if underscore_index > 0:     
        return name_str[0:underscore_index]
    else:
        return name_str
    
	
def create_new_image_path(base_image_path, output_dir, output_suffix):
    """Create a new path string based on the pre-modification image path,
    an output directory, and the new output suffix to rename the file with"""
    base_name = get_base_file_name(base_image_path)
    
    new_name = base_name + '_' + output_suffix + '.tif'
        
    new_path = os.path.join(output_dir, new_name)
    return new_path
    

def find_shared_images(dir_one, dir_two):
    """Base image names derived from directory one, are mapped to images from
    directory two."""
    
    #todo: modify dir_one_baseFile_names into a list of names, and then
    #implement a .txt file?
    
    #todo: make a check for different categories of name,
    #   if there are multiple instances of a single name?
    
    file_list_one = [f for f in os.listdir(dir_one) if f.endswith('.tif')]
    file_list_two = [f for f in os.listdir(dir_two) if f.endswith('.tif')]
        
    dir_one_image_paths = list()
    dir_two_image_paths = list()

    for i in range(0,len(file_list_one)):
        base_nameOne = get_base_file_name(file_list_one[i])
        
        for j  in range(0,len(file_list_two)):
            base_nameTwo = get_base_file_name(file_list_two[j])
          
            if base_nameOne == base_nameTwo:
                
                dir_one_image_paths.append(dir_one + file_list_one[i])
                dir_two_image_paths.append(dir_two + file_list_two[j])

    
    return (dir_one_image_paths, dir_two_image_paths)