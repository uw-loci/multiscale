import os
import csv
import mp_img_manip.utility_functions as util
import pandas as pd

    
def read_write_pandas_row(file_path, index, index_label, column_labels):
        
    (file_dir, file_name) = os.path.split(file_path)

    try:
        data = pd.read_csv(file_path, index_col = index_label)
        try:
            return data.loc[index]
        except:
            print('There are no existing entries for ' + index )
    except:
        print('Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(index = pd.Index([], dtype='object', name=index_label),  columns = column_labels)
    
    print('Please enter in values for {0}'.format(index))
    new_row = [input(x + ': ') for x in column_labels]
    data.loc[index] = new_row 
    
    data.to_csv(file_path)
        
    return data.loc[index]
        
        
def write_pandas_row(file_path, index, index_label, column_labels, column_values):
        
    (file_dir, file_name) = os.path.split(file_path)

    try:
        data = pd.read_csv(file_path, index_col = index_label)
    except:
        print('Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(index = pd.Index([], dtype='object', name=index_label),  columns = column_labels)
    
    data.loc[index] = column_values
    data.to_csv(file_path)
        


def getBaseFileName(fileName):
    """This function extracts the 'base name' of a file, which is defined as
    the string up until the first underscore, or until the extension if
    there is no underscore"""
    
    fullFileName = os.path.split(fileName)[1]
    
    nameStr = os.path.splitext(fullFileName)[0]
    
    underscoreIndexes = nameStr.find('_')
    
    if underscoreIndexes > 0:     
        return nameStr[0:underscoreIndexes]
    else:
        return nameStr
    
def createNewImagePath(baseImgPath, outputDir, outputSuffix):
    """Create a new path string based on the pre-modification image path,
    an output directory, and the new output suffix to rename the file with"""
    baseName = getBaseFileName(baseImgPath)
    
    newName = baseName + outputSuffix + '.tif'
        
    newPath = os.path.join(outputDir, newName)
    return newPath
    

def findSharedImages(dirOne, dirTwo):
    """Base image names derived from directory one, are mapped to images from
    directory two."""
    
    #todo: modify dirOne_baseFileNames into a list of names, and then
    #implement a .txt file?
    
    #todo: make a check for different categories of name, if there are multiple instances of a single name?
    
    fileListOne = [f for f in os.listdir(dirOne) if f.endswith('.tif')]
    fileListTwo = [f for f in os.listdir(dirTwo) if f.endswith('.tif')]
        
    dirOneImagePaths = list()
    dirTwoImagePaths = list()

    for i in range(0,len(fileListOne)):
        baseNameOne = getBaseFileName(fileListOne[i])
        
        for j  in range(0,len(fileListTwo)):
            baseNameTwo = getBaseFileName(fileListTwo[j])
          
            if baseNameOne == baseNameTwo:
                
                dirOneImagePaths.append(dirOne + fileListOne[i])
                dirTwoImagePaths.append(dirTwo + fileListTwo[j])

    
    return (dirOneImagePaths, dirTwoImagePaths)