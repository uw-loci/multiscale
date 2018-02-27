import os as os

def getBaseFileName(fileName):
    """This function extracts the 'base name' of a file, which is defined as
    the string up until the first underscore, or until the extension if
    there is no underscore"""
    
    #Eliminate the folder path, if there is any
    (None, fullFileName) = os.path.split(fileName)
    
    (nameStr, None) = os.path.splitext(fullFileName)
    
    underscoreIndexes = nameStr.find('_')
    
    if underscoreIndexes:     
        baseNameIndex = underscoreIndexes-1
        baseName = nameStr[0:baseNameIndex]
    else:
        baseName = nameStr

    return baseName