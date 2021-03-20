# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 14:11:17 2021

@author: tvdrb
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io, filters
import cv2

# =============================================================================
# Automatic pipette focus v2
# =============================================================================

# load tiff
filepath = r"C:\Users\tvdrb\Desktop\Thijs\Z stack.tif"
I = io.imread(filepath)


def cropImage(imagestack,xpos,ypos,xsize,ysize):
    """
    This image crops the input in X and Y for every Z.
    """
    # get depth of image stack
    depth = imagestack.shape[0]
    
    # crop Z stack in the XY-plane
    cropped = np.empty((depth,ysize,xsize))
    for i in range(depth):
        left = round(xcenter - xsize/2)
        right = round(xcenter + xsize/2)
        up = round(ycenter - ysize/2)
        down = round(ycenter + ysize/2)
        cropped[i,:,:] = imagestack[i,up:down,left:right]
     
    return cropped


def outoffocusPenalty(img):
    """
    This functions calculates a penalty score that is minimum for sharp images.
    """
    # average images
    img_average = filters.gaussian(img, 5)
    
    # calculate laplacian
    img_laplace = filters.laplace(img_average, 3)
    
    # calculate variance
    penalty = np.var(img_laplace)
    
    return penalty


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
    image = cv2.GaussianBlur(image, (13, 13), 3)
   
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


# get image stack dimensions
depth = I.shape[0]
height = I.shape[1]
width = I.shape[2]

# crop image
print("Cropping images...")
xcenter = width/2
ycenter = height/2 - 50
xsize = 204
ysize = 204
Icropped = cropImage(I, xcenter, ycenter, xsize, ysize)

# calculate focus penalty
print("Calculating penalties...")
variance = np.empty(depth)
variance_Xin = np.empty(depth)
for i in range(depth):
    variance[i] = outoffocusPenalty(Icropped[i,:,:])
    variance_Xin[i] = variance_of_laplacian(Icropped[i,:,:])
    if i == 25:
        plt.matshow(Icropped[i,:,:], cmap='gray')

# manually saved z positions
zpos = np.concatenate([np.arange(-300, -250, 50),
                        np.arange(-250, -100, 25),
                        np.arange(-100, -50, 10),
                        np.arange(-50, -3, 1),
                        np.arange(-3, -2.5, 0.5),
                        np.arange(-2.5, 5, 0.1),
                        np.arange(5, 50.001, 1),
                        np.arange(70, 100, 10),
                        np.arange(100, 250, 25),
                        np.arange(250, 500, 50),
                        np.arange(500, 2000.001, 100)])
# zpos = np.concatenate([np.arange(-350, -250, 50),
#                        np.arange(-250, -100, 25),
#                        np.arange(-100, -50, 10),
#                        np.arange(-50, -10.001, 5),
#                        np.arange(0, 5.001, 1),
#                        np.arange(5, 100, 10),
#                        np.arange(100, 500, 50),
#                        np.arange(500, 1000, 100),
#                        np.arange(1000, 2000, 250),
#                        np.arange(2000, 3000.001, 500)])

# plot figures
fig, axs = plt.subplots(1,2)
axs[0].plot(zpos,variance)
axs[0].set_title('Autofocus Thijs')
axs[0].set_xlabel(r'Focus depth (in $\mu$m)')
axs[0].set_ylabel(r'Variance of Laplacian (a.u.)')
axs[1].plot(zpos,variance_Xin)
axs[1].set_title('Autofocus Xin')
axs[1].set_xlabel(r'Focus depth (in $\mu$m)')
axs[1].set_ylabel(r'Variance of Laplacian (a.u.)')
