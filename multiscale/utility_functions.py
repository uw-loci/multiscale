# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:59:49 2018

@author: mpinkert
"""
import os
from pathlib import Path
from PIL import Image
import warnings
import shutil
import json

warnings.simplefilter('ignore', Image.DecompressionBombWarning)


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


