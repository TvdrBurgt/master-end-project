# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 21:09:43 2021

@author: tvdrb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Tool for quantitatively comparing pipette tip estimates
# =============================================================================


# target folder containing the images to be annotated
path = r'C:\Users\tvdrb\Desktop\Thijs\Translation space'

# names of files to compare
file1 = "Translation space attenuated"
file2 = "Translation space Boyden"

# read files
file1 = pd.read_csv(path+"\\"+file1, sep=';')
file2 = pd.read_csv(path+"\\"+file2, sep=';')


# calculate position differences
name = []
x1 = []
x2 = []
y1 = []
y2 = []
dx = []
dy = []
for index, row in file1.iterrows():
    if row[0] == file2.filename[index]:
        name.append(row[0])
        x1.append(row[1])
        y1.append(row[2])
        x2.append(file2.x[index])
        y2.append(file2.y[index])
        dx.append(row[1] - file2.x[index])
        dy.append(row[2] - file2.y[index])
    else:
        print("Filename does not correspond:\n{}".format(row[0]))

# create new datafile containing all information
combinedfile = pd.DataFrame(list(zip(name,x1,y1,x2,y2,dx,dy)),
                            columns =['Filename','x1','y1','x2','y2','dx','dy'])

# make scatter plot out of coordinates
"""
Make scatter plot (x1,y1) together with (x2,y2) with corresponding colors.
Do someting with dx and dy
"""
plt.plot(dy)

