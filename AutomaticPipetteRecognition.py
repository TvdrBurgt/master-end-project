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
from PipetteRecognition import detectPipettetip


class DetectPipetteTips:
    """"
    This class iterates through a folder containing .tif files and extracts the
    (x,y)-coordinates of pipette tips.
    """
    def __init__(self,path,plotfile=''):
        self.folder = path              # folder containing the images
        self.pipettetips = []           # list to save pipette tip coordinates
        self.difficultimages = []       # list of images where algorithm fails
        self.plotfile = plotfile        # this file will be plotted
        self.upper_angle = 97.5         # only for first calibration
        self.lower_angle = 82.5         # only for first calibration
        self.pipettediameter = 16.5     # only for first calibration
        
        
    def iterator(self):
        """
        This function iterates over all files in the specified folder unless a
        filename is given, in this case it will open that file for plotting only
        """
        # extract filenames
        filenames = os.listdir(self.folder)
        num_files = len(filenames)
        
        # skip all images instead of the one you want to plot
        if not self.plotfile:
            self.plotflag = False
        else:
            filenames = [self.plotfile,'']
            num_files = 1
            self.plotflag = True
        
        # iterate over all files
        for index,filename in enumerate(filenames):
            
            # read image
            if filename.endswith('.tif'):
                I = io.imread(self.folder + '\\' + filename)
                print("\nFile number %d/%d" % (index+1,num_files))
            else:
                continue
            
            # pipette tip detection algorithm
            x1, y1 = detectPipettetip(I,
                                      self.upper_angle,
                                      self.lower_angle,
                                      self.pipettediameter,
                                      blursize=15,
                                      angle_range=10,
                                      num_angles=1000,
                                      num_peaks=8,
                                      plotflag=self.plotflag)
            
            # crop image
            Icropped, xref, yref, faultylocalisation = self.cropImage(I, x1, y1)
            
            # assign (x,y)=(nan,nan) as coordinate if Icropped is fully outside I
            if faultylocalisation:
                self.difficultimages.append([filename])
                self.pipettetips.append([filename, (np.nan, np.nan)])
                continue
            
            # pipette tip detection algorithm
            x2, y2 = detectPipettetip(Icropped,
                                      self.upper_angle,
                                      self.lower_angle,
                                      self.pipettediameter,
                                      blursize=4,
                                      angle_range=10,
                                      num_angles=5000,
                                      num_peaks=6,
                                      plotflag=self.plotflag)
            
            # adjusting x2 and y2 with the reference coordinates
            x = xref + x2
            y = yref + y2
            
            # saving pipette tip coordinates
            print('Pipette tip detected @ (x,y) = (%f,%f)' % (x,y))
            self.pipettetips.append([filename, (x, y)])
            
    
    def cropImage(self,I,xpos,ypos,xsize=600,ysize=150):
        """
        This functions crops the input figure around the coordinates from the
        first tip detection algorithm.
        """
        
        # round pipette coordinates to integers
        xpos = np.round(xpos)
        ypos = np.round(ypos)
        
        # specify cropping region
        left = int(xpos-xsize/2)
        right = int(xpos+xsize/2)
        up = int(ypos-ysize/2)
        down = int(ypos+ysize/2)
        
        # check if the cropping exceeds image boundaries
        faultylocalisation = False
        height = I.shape[0]
        width = I.shape[1]
        if left < 0:
            left = 0
            if right < 0:
                right = xsize
                faultylocalisation = True
        if right > width-1:
            right = width-1
            if left > width-1:
                left = width-1 - xsize
                faultylocalisation = True
        if up < 0:
            up = 0
            if down < 0:
                down = ysize
                faultylocalisation = True
        if down > height-1:
            down = height-1
            if up > height-1:
                up = height-1 - ysize
                faultylocalisation = True
        
        # crop image
        Icropped = I[up:down,left:right]
        
        # reference point (x0,y0) is (0,0) in the cropped image
        x0 = left
        y0 = up
        
        return Icropped, x0, y0, faultylocalisation
                
        
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
    path = r"C:\Users\tvdrb\Desktop\Thijs\XY grid\2021-03-23"
    savename = "XY grid 2021-03-23 algorithm"
    
    imagefolder = DetectPipetteTips(path)
    imagefolder.iterator()
    imagefolder.save2file(savename)
    