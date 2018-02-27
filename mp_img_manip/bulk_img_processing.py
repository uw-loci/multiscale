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