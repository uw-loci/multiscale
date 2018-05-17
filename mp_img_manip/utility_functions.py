# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:59:49 2018

@author: mpinkert
"""
import os
from pathlib import Path


def item_present_all_lists(item, lists):
    """Check if an item is present in all lists"""
    for index in range(len(lists)):
        if item not in lists[index]:
            return False
        
    return True

# def append_item_index_to_lists(item, lists, index_lists):
#    
#    for index in range(len(lists)):
#        item_index = lists[index].index(item)
#        index_lists[index].append(item_index)
#        
#    return index_lists


def list_filetype_in_subdirs(base_dir, file_ext):
    """Find all files in the immediate subdirectores with a given extension
    
    base_dir - immediate dir to find subdirs of
    file_ext - the file extension to search for
    
    output: file_list - a list of the relevant file paths """
    dir_list = [d[0] for d in os.walk(base_dir)]
    
    file_list = []
    
    for subdir in dir_list:
        subdir_list = list_filetype_in_dir(subdir, file_ext)
        file_list.extend(subdir_list)
     
    return file_list


def list_filetype_in_dir(file_dir, file_ext):
    """Given a directory path, return all files of given file type as a list"""
    return [Path(file_dir, f) for
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

    
    