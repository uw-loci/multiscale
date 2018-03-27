# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:59:49 2018

@author: mpinkert
"""
import os

def item_present_all_lists(item, list_of_lists):
    """Check if an item is present in all lists"""
    for index in range(len(list_of_lists)):
        if item not in list_of_lists[index]:
            return False
        
    return True

def file_type_in_dir(file_dir, file_ext):
    """Given a directory path, return all tifs in the directory as a list"""
    return [os.path.join(file_dir, f) for
                  f in os.listdir(file_dir) if f.endswith(file_ext)]  
    
def query_int(message):
  """Ask the user for an integer"""
  while True:
    try:
       user_input = int(input(message))       
    except ValueError:
       print("Please enter a valid integer.")
       continue
    else:
       return user_input 
       break 

def query_float(message):
    """Ask the user for a float"""
   
    while True:
        try:
            user_input = float(input(message))
        except ValueError:
            print("Please enter a valid float.")
        else:
            return user_input
            break

def yes_no(question):
    """Ask the user a yes/no question"""
    
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
     
    while True:
        choice = input(question).lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           print("Please respond with 'yes' or 'no'\n")
           
def character_indices(string, char):
    """Find all indices in a string corresponding to a character"""
    return [i for i, ltr in enumerate(string) if ltr == char]
    
    
def query_str_list(numStrs, message, strType = 'String'):
    """Ask the user for multiple strings"""
    print(message)
    return [input(strType + ' ' + str(x+1) + ': ') for x in range(numStrs)]
    
def query_float_list(valueNames):
    """Ask the user for a list of floats"""
    return [query_float(value + ': ') for value in valueNames]

    
    