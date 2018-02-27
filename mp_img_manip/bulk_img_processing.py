import os as os

def getBaseFileName(fileName):
    """This function extracts the 'base name' of a file, which is defined as
    the string up until the first underscore, or until the extension if
    there is no underscore"""
    
    fullFileName = os.path.split(fileName)[1]
    
    nameStr = os.path.splitext(fullFileName)[0]
    
    underscoreIndexes = nameStr.find('_')
    
    if underscoreIndexes:     
        return nameStr[0:underscoreIndexes]
    else:
        return nameStr
