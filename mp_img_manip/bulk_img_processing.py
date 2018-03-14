import os
import csv
import mp_img_manip.utility_functions as util
import pandas as pd

def read_write_column_file(imgPath, fileName, numColumns = 3):
    """"Read in a file that specifies a name, and a number"""
    
    #Bug: Writes an extra line before the new row
    #todo: Add a way to update values
    
    (imgDir, imgName) = os.path.split(imgPath)
    
    
    with open(imgDir + '/' + fileName, 'a+') as file:
        reader = csv.reader(file)
        writer = csv.writer(file)

        file.seek(0)

        try:
            header = next(reader)
        except StopIteration:
            message = 'Creating new file ' + fileName + ' in ' + imgDir 
            header = util.query_str_list(numColumns, message , 'Header')
            writer.writerow(header)
            
        
        for row in reader:
            if row[0] == imgName:
                return row
       
        print('There are no existing values for ' + imgName)
        
        new_row = [imgName]
        new_row.extend(util.query_float_list(header[1:]))
        
        #bug: This next line writes a blank row first.  
        
        writer.writerow(new_row)
        
        return new_row
    
    
    
def read_write_pandas_row(file_path, index, index_label, column_labels):
        
    (file_dir, file_name) = os.path.split(file_path)

    try:
        data = pd.read_csv(file_dir + '/' + file_name, index_col = index_label)
        file_exists = True
        try:
            return data.loc[index]
        except:
            print('There are no existing entries for ' + index )
    except:
        file_exists = False
        print('Creating new file ' + file_name + ' in ' + file_dir)
        data = pd.DataFrame(index = pd.Index([], dtype='object', name=index_label),  columns = column_labels)
    
    print('Please enter in values for {0}'.format(index))
    new_row = [input(x + ': ') for x in column_labels]
    data.loc[index] = new_row 
    
    if not file_exists:
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