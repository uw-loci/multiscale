"""
The previous versions of the code used a custom function to save transforms as pandas csvs.  This method is more
complicated and prone to error than SimpleITKs native method, as I need to specify a version for each possible
transform.

This script is meant to convert transforms made using the old pandas method into the native SimpleITK method.
"""

