# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 14:11:17 2021

@author: tvdrb
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io, filters
import cv2
import time

# =============================================================================
# Automatic pipette focus v2
# =============================================================================

# load tiff
filepath = r"C:\Users\tvdrb\Desktop\Thijs\Z stack.tif"
I = io.imread(filepath)


import scipy.stats as st
def gkern(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel."""

    x = np.linspace(-nsig, nsig, kernlen+1)
    kern1d = np.diff(st.norm.cdf(x))
    kern2d = np.outer(kern1d, kern1d)
    return kern2d/kern2d.sum()


def makeGaussian(size, fwhm = 3, center=None):
    """ Make a square gaussian kernel.
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """

    x = np.arange(0, size, 1, float)
    y = x[:,np.newaxis]
    
    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]
    
    return np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)


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

# constructing Gaussian kernel
kernel = gkern(2048,5)
kernel = makeGaussian(2048, fwhm=256)

# calculate focus penalty in a confined region
print("Calculating penalties...")
variance = np.empty(depth)
variance_Xin = np.empty(depth)
for i in range(depth):
    start = time.time()
    IK = I[i] * kernel
    variance[i] = outoffocusPenalty(IK)
    variance_Xin[i] = variance_of_laplacian(IK)
    print(time.time()-start)

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
