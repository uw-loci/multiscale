# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:59:49 2018

@author: mpinkert
"""
import os

def query_int(message):

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
    
    while True:
        try:
            user_input = float(input(message))
        except ValueError:
            print("Please enter a valid float.")
        else:
            return user_input
            break

def yes_no(question):
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
           
    