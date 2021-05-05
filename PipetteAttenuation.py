# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 16:35:11 2021

@author: tvdrb
"""
import matplotlib.pyplot as plt
import os
from skimage import io


# =============================================================================
# Tool for pipette tip annotation
# =============================================================================


# target folder containing the images to be annotated
path = r'C:\Users\tvdrb\Desktop\Thijs\XY grid\2021-03-23'

# name of .txt in which to save pipette coordinates
savename = 'XY grid 2021-03-23 attenuated'

# list to save the pipette tip coordinates in
coordinateclicks = []
finallist = []


def on_click(event):
    # register pixel position of mouse click
    ix = round(event.xdata)
    iy = round(event.ydata)
    
    coordinateclicks.append((ix, iy))
    print('You pressed: (x,y)={}'.format(coordinateclicks[-1]))


# iterate over all .tif files in the target folder
for count, filename in enumerate(os.listdir(path)):
    if filename[-4:] == '.tif':
        print(filename)
        
        # initiate figure where to select pixels from and display images
        fig = plt.figure()
        cid = fig.canvas.mpl_connect('button_press_event', on_click)
        
        # read image
        I = io.imread(path + "\\" + filename)
        
        # plot image
        plt.imshow(I, cmap='gray')
        plt.tight_layout()
        plt.axis('image')
        plt.axis('off')
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        
        # block for-loop untill figure is closed
        plt.show(block=True)

        # adjust for multiple clicks by removing all but the last click
        finallist.append([filename, coordinateclicks[-1]])
        print('Last annotated: {}'.format(finallist[-1]))
    
# write final coordinates to a .csv file
with open(path+'\\'+savename, 'w') as txtfile:
    txtfile.write("filename;x;y\n")
    for item in finallist:
        txtfile.write("{};".format(item[0]))
        txtfile.write("%d;" % item[1][0])
        txtfile.write("%d\n" % item[1][1])
