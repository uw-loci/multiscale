# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:59:49 2018

@author: mpinkert
"""
import os
from pathlib import Path
import shutil
import json
import scipy.io as sio
import numpy as np


def write_json(dictionary: dict, path_dict: Path):
        with open(str(path_dict), 'w') as file:
                json.dump(dictionary, file)


def read_json(path_dict: Path):
        with open(str(path_dict), 'r') as file:
                dictionary = json.load(file)
                return dictionary


def move_files_to_new_folder(list_files: list, dir_new: Path):
        os.makedirs(dir_new, exist_ok=True)
        for file in list_files:
                new_path = Path(dir_new, file.name)
                shutil.move(file, new_path)


def item_present_all_lists(item, lists: list):
        """Check if an item is present in all lists"""
        for index in range(len(lists)):
                if item not in lists[index]:
                        return False
        
        return True


def list_filetype_in_dir(file_dir: Path, file_ext: str):
        """Given a directory path, return all files of given file type as a list"""
        return [Path(file_dir, f) for f in os.listdir(file_dir) if f.endswith(file_ext)]


def list_filetype_in_subdirs(base_dir: Path, file_ext: str):
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


def query_int(message: str):
        """Ask the user for an integer"""
        while True:
                try:
                        user_input = int(input(message))
                except ValueError:
                        print("Please enter a valid integer.")
                        continue
                else:
                        return user_input


def query_float(message: str):
        """Ask the user for a float"""
        while True:
                try:
                        user_input = float(input(message))
                except ValueError:
                        print("Please enter a valid float.")
                        continue
                else:
                        return user_input


def query_str(message: str):
        """Ask the user for a float"""
        while True:
                try:
                        user_input = input(message)
                except ValueError:
                        print("Please enter a valid string.")
                        continue
                else:
                        return user_input


def query_yes_no(question: str):
        """Ask the user a yes/no question"""
        
        yes = {'yes', 'y', 'ye'}
        no = {'no', 'n'}
        
        while True:
                choice = input(question).lower()
                if choice in yes:
                        return True
                elif choice in no:
                        return False
                else:
                        print("Please respond with 'yes' or 'no'\n")


def character_indices(string: str, char: str):
        """Find all indices in a string corresponding to a character"""
        return [i for i, ltr in enumerate(string) if ltr == char]


def query_str_list(str_names: list):
        """Ask the user for multiple strings"""
        return [query_str(string + ': ') for string in str_names]


def query_float_list(valueNames: list):
        """Ask the user for a list of floats"""
        return [query_float(value + ': ') for value in valueNames]


def split_list_into_sublists(large_list: list, size_of_sublist: int):
        for i in range(0, len(large_list), size_of_sublist):
                yield large_list[i:i + size_of_sublist]


def load_mat(file_path, variables=None):
        '''
            this function should be called instead of direct spio.loadmat
            as it cures the problem of not properly recovering python dictionaries
            from mat files. It calls the function check keys to cure all entries
            which are still mat-objects
            '''

        file_name = str(file_path)

        def _check_keys(d):
                '''
                checks if entries in dictionary are mat-objects. If yes
                todict is called to change them to nested dictionaries
                '''
                for key in d:
                        if isinstance(d[key], sio.matlab.mio5_params.mat_struct):
                                d[key] = _todict(d[key])
                return d

        def _todict(matobj):
                '''
                A recursive function which constructs from matobjects nested dictionaries
                '''
                d = {}
                for strg in matobj._fieldnames:
                        elem = matobj.__dict__[strg]
                        if isinstance(elem, sio.matlab.mio5_params.mat_struct):
                                d[strg] = _todict(elem)
                        elif isinstance(elem, np.ndarray):
                                d[strg] = _tolist(elem)
                        else:
                                d[strg] = elem
                return d

        def _tolist(ndarray):
                '''
                A recursive function which constructs lists from cellarrays
                (which are loaded as numpy ndarrays), recursing into the elements
                if they contain matobjects.
                '''
                elem_list = []
                for sub_elem in ndarray:
                        if isinstance(sub_elem, sio.matlab.mio5_params.mat_struct):
                                elem_list.append(_todict(sub_elem))
                        elif isinstance(sub_elem, np.ndarray):
                                elem_list.append(_tolist(sub_elem))
                        else:
                                elem_list.append(sub_elem)
                return elem_list

        if variables is None:
                data = sio.loadmat(file_name, struct_as_record=False, squeeze_me=True)
        else:
                data = sio.loadmat(file_name, struct_as_record=False, squeeze_me=True, variable_names=variables)
        return _check_keys(data)

