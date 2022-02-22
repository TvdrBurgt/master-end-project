# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:17:08 2021

@author: tvdrb
"""

import os
import numpy as np
from skimage import io


# =============================================================================
# Automatic Pipette Recognition
# =============================================================================

# load function from other file
from PipetteRecognition import detectPipettetip, makeGaussian


class DetectPipetteTips:
    """"
    This class iterates through a folder containing .tif files and extracts the
    (x,y)-coordinates of pipette tips.
    """
    def __init__(self,path,plotfile=''):
        self.folder = path              # folder containing the images
        self.pipettetips = []           # list to save pipette tip coordinates
        self.plotfile = plotfile        # this file will be plotted
        self.pipettediameter = 16       # only for first calibration
        self.orientation = 0            # pipette orientation in degrees
        self.plotflag = False
        
        
    def iterator(self):
        """
        This function iterates over all files in the specified folder unless a
        filename is given, in this case it will open that file for plotting only
        """
        # extract filenames
        filenames = os.listdir(self.folder)
        num_files = len(filenames)
        
        # iterate over all files
        for index, filename in enumerate(filenames):
            
            # read image
            if filename.endswith('a.tif'):
                name = filename[:-5]
                Ia = io.imread(self.folder + '\\' + name + 'a.tif')
                Ib = io.imread(self.folder + '\\' + name + 'b.tif')
                print("\nFile number %d out of %d" % (index+1, num_files))
            else:
                continue
            
            try:
                # pipette tip detection algorithm
                x1, y1 = detectPipettetip(Ia, Ib, diameter=16, orientation=0)
        
                # apply Gaussian window
                W = makeGaussian(size=Ia.shape, mu=(x1,y1), sigma=(Ia.shape[0]//12,Ia.shape[1]//12))
                IaW = np.multiply(Ia,W)
                IbW = np.multiply(Ib,W)
                
                # pipette tip detection algorithm
                x,y = detectPipettetip(IaW, IbW, diameter=20, orientation=0)
            except:
                x,y = (np.nan,np.nan)
                print('something went wrong...')
            
            # saving pipette tip coordinates
            print('Pipette tip detected @ (x,y) = (%f,%f)' % (x,y))
            self.pipettetips.append([filename, (x, y)])
    
        
    def save2file(self,savename):
        """
        This function writes the pipette tip coordinate list to a .csv file
        """
        with open(self.folder+'\\'+savename, 'w') as txtfile:
            txtfile.write("filename;x;y\n")
            for item in self.pipettetips:
                txtfile.write("{};".format(item[0]))
                txtfile.write("%f;" % item[1][0])
                txtfile.write("%f\n" % item[1][1])
        print("\nFiles saved as: '{}'".format(savename))



if __name__ == '__main__':
    path = r"C:\Users\tvdrb\Desktop\2022-02-11 @ focus @ +30mBar"
    savename = "2022-02-11 @ focus @ +30mBar algorithm"
    
    imagefolder = DetectPipetteTips(path)
    imagefolder.iterator()
    imagefolder.save2file(savename)
    