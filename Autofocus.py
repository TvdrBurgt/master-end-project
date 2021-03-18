# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 16:32:09 2021

@author: tvdrb
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io
import cv2


# =============================================================================
# Automatic pipette focus
# =============================================================================

def variance_of_laplacian(image):
    """
    Compute the Laplacian of the image and then return the focus
    measure, which is simply the variance of the Laplacian       
 
    Parameters
    ----------
    image : np.array
        Gray scale input image.
 
    Returns
    -------
    sharpness : float
        Sharpness of the image, the higher the better.
 
    """
    # if image.shape[2] == 3:
    #     image = rgb2gray(image)
   
    # Blur the image a bit.
    image = cv2.GaussianBlur(image, (13, 13), 0)
   
    # convolution of 3 x 3 kernel, according to different datatype.
    if type(image[0,0])==np.float32:
        sharpness = cv2.Laplacian(image, cv2.CV_32F).var()
    elif type(image[0,0])==np.float64:
        sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
    elif type(image[0,0])==np.uint8:
        sharpness = cv2.Laplacian(image, cv2.CV_8U).var()
    elif type(image[0,0])==np.uint16:
        sharpness = cv2.Laplacian(image, cv2.CV_16U).var()
       
    return sharpness


# load tiff
filepath = r"C:\Users\tvdrb\Desktop\Thijs\Z stack.tif"
I = io.imread(filepath)

# extract image dimensions
depth = I.shape[0]
height = I.shape[1]
width = I.shape[2]

# crop image
xcenter = width/2
ycenter = height/2 - 40
xsize = 2048
ysize = 128
Icropped = np.empty((depth,ysize,xsize))

# crop Z stack in the XY-plane
for i in range(depth):
    left = round(xcenter - xsize/2)
    right = round(xcenter + xsize/2)
    up = round(ycenter - ysize/2)
    down = round(ycenter + ysize/2)
    Icropped[i,:,:] = I[i,up:down,left:right]

# iterate over Z stack
variance = np.empty(depth)
for i in range(depth):
    variance[i] = variance_of_laplacian(Icropped[i,:,:])
    print(variance[i])

# set z positions
zpos = np.concatenate([np.arange(-300, -250, 50),
                       np.arange(-250, -100, 25),
                       np.arange(-100, -50, 10),
                       np.arange(-50, -3, 1),
                       np.arange(-3, -2.5, 0.5),
                       np.arange(-2.5, 5, 0.1),
                       np.arange(5, 50, 1),
                       np.arange(50, 100, 10),
                       np.arange(100, 250, 25),
                       np.arange(250, 500, 50),
                       np.arange(500, 2001, 100)])

plt.plot(zpos,variance)
plt.show()

plt.matshow(Icropped[85,:,:],cmap='gray')
