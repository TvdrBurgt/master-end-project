# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 21:05:39 2021

@author: tvdrb
"""

import os


# =============================================================================
# Tool for renaming images without timestamp
# =============================================================================

filepath = r'W:\staff-groups\tnw\ist\do\projects\Neurophotonics\Brinkslab\Data\Thijs\XY grid\2021-03-23'

yestoall = False
notoall = False
for count, oldfilename in enumerate(os.listdir(filepath)):
    
    # split filename with delimiter '_' and '.'
    filename = oldfilename.split('_')[0]
    filetype = oldfilename.split('.')[-1]
    
    # construct new filename as: [filename].[filetype]
    if filename == oldfilename:
        newfilename = filename
    else:
        newfilename = filename + '.' + filetype
    
    # manual check
    print("\nAre you sure you want to rename:")
    print(oldfilename + '  -->  ' + newfilename)
    if not yestoall:
        x = input("[y]/n\n")
        if x == 'yes to all':
            yestoall = True
        elif x == 'no to all':
            break
    
    # rename filename if filename is unique
    if x == 'y' or x == 'yes' or yestoall:
        try:
            os.rename(filepath+'/'+oldfilename, filepath+'/'+newfilename)
        except:
            print("File name is not unique: {}".format(newfilename))
            break
    
