# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:17:08 2021

@author: tvdrb
"""

import numpy as np
from skimage import io, filters, feature, transform, draw
import matplotlib.pyplot as plt


# =============================================================================
# Pipette Recognition (based on Boyden et al.'s autopatcher IG)
# =============================================================================

# load tiff
I = io.imread('../pipette tips/focus 0 100 0.tif')


# if I.shape[2] == 3:
#     # check if tiff is a grayscale image
#     if np.sum(I[:,:,0]==I[:,:,1]) == I.shape[0]*I.shape[1]:
#         if np.sum(I[:,:,1]==I[:,:,2]) == I.shape[0]*I.shape[1]:
#             I = I[:,:,0]
#             print('Tiff converted to grayscale...\n')
        

####################### tip detection algorithm #######################
def Houghlines2Imageboundary(T,R,img):
    """
    This function extracts the intersection coordinates between extended Hough-
    lines with the image boundary. The output are the rows and columns of the
    image where the infinite Houghlines leave/enter the image.
    """
    # get width and height of image
    height = img.shape[0]
    width = img.shape[1]
    
    # divide angles into parallel and perpundicular to prevent exploding slopes
    cutoff = np.abs(np.sin(T))
    Tpar = T[np.where(cutoff >= np.sqrt(2)/2)]
    Tperp = T[np.where(cutoff < np.sqrt(2)/2)]
    
    # determine a and b in y=ax+b
    a = np.tan(np.pi/2+Tpar)
    b = R/np.sin(Tpar)
    
    # prevent dividing by zero in the next step
    a[a==0] = 1e-9
    
    # determine crossings with the lines: y=0, x=0, y=height, x=width
    x0 = -b/a
    y0 = b
    xh = (height-b)/a
    yw = a*width + b
    
    # place crossings on the image edge
    x0[x0>width-1] = width-1
    x0[x0<0] = 0
    y0[y0>height-1] = height-1
    y0[y0<0] = 0
    xh[xh>width-1] = width-1
    xh[xh<0] = 0
    yw[yw>height-1] = height-1
    yw[yw<0] = 0
    
    # match coordinates
    xleft = np.zeros((len(Tpar)))
    yleft = np.zeros((len(Tpar)))
    xright = np.zeros((len(Tpar)))
    yright = np.zeros((len(Tpar)))
    for i in range(len(Tpar)):
        xleft[i] = np.min([x0[i],xh[i]])
        xright[i] = np.max([x0[i],xh[i]])
        if a[i] > 0:
            yleft[i] = np.min([y0[i],yw[i]])
            yright[i] = np.max([y0[i],yw[i]])
        else:
            yleft[i] = np.max([y0[i],yw[i]])
            yright[i] = np.min([y0[i],yw[i]])
            
    # let x and y be rows and columns
    c0 = np.around(xleft).astype(int)
    r0 = np.around(yleft).astype(int)
    c1 = np.around(xright).astype(int)
    r1 = np.around(yright).astype(int)
    
    return r0, c0, r1, c1

# Gaussian blur
print('Gaussian blurring...\n')
IB = filters.gaussian(I, 15)

# Canny edge detection
print('Canny edge detection...\n')
BW = feature.canny(IB, sigma=10, low_threshold=0.9, high_threshold=0.7, use_quantiles=True)

# Hough transform
print('Calculating Hough transform...\n')
H, T, R = transform.hough_line(BW,np.linspace(np.pi/3,2*np.pi/3,120*10))

# extract most common lines in the image from the Hough transform
print('Finding most common lines from Hough transform...\n')
num_lines = 7
_, Tcommon, Rcommon = transform.hough_line_peaks(H,T,R,num_peaks=num_lines)

# draw Houghlines on a canvas with same dimensions as the input image
print('Filling canvas with most the %d most common lines...\n' % num_lines)
canvas = np.zeros((I.shape[0], I.shape[1]))
for r0, c0, r1, c1 in zip(*Houghlines2Imageboundary(Tcommon,Rcommon,I)):
    # use line_aa() instead of line() because the rows and columns are rounded floats
    rr, cc = draw.line(r0, c0, r1, c1)
    # update canvas
    canvas[rr, cc] += 1
# make lines thicker with gaussian blur
canvasblur = filters.gaussian(canvas, 15)

# extract pipette tip
ypos, xpos = np.where(canvasblur == np.max(canvasblur))
print('Pipette tip located at pixel coordinate: (x,y) = (%d,%d).' % (xpos,ypos))

#######################################################################


# make figures
f1, axs1 = plt.subplots(1,3)
axs1[0].imshow(I, cmap='gray'); axs1[0].axis('image'); axs1[0].axis('off')
axs1[1].imshow(canvasblur, cmap='gray'); axs1[1].axis('image'); axs1[1].axis('off')
axs1[2].imshow(I, cmap='gray'); axs1[2].axis('image'); axs1[2].axis('off')
axs1[2].scatter(x=xpos, y=ypos, c='r', s=30)
axs1[2].annotate('(%d,%d)' % (xpos,ypos), (xpos+30, ypos-15), c='r')

f2, axs2 = plt.subplots(1,3)
axs2[0].imshow(IB, cmap='gray', aspect = 'auto'); axs2[0].axis('image'); axs2[0].axis('off')
axs2[1].imshow(BW, cmap='jet', aspect = 'auto'); axs2[1].axis('image'); axs2[1].axis('off')
axs2[2].imshow(np.log(1+H), extent=[np.rad2deg(T[0]), np.rad2deg(T[-1]), R[-1], R[0]], aspect='auto')
axs2[2].set_xlabel(r'$\theta$ (radians)')
axs2[2].set_ylabel(r'$\rho$ (pixels)')

for _, angle, dist in zip(*transform.hough_line_peaks(H,T,R,num_peaks=num_lines)):
    (x0, y0) = dist*np.array([np.cos(angle), np.sin(angle)])
    axs1[0].axline((x0 ,y0), slope=np.tan(angle + np.pi/2))
    axs2[2].scatter(x=[angle*180/np.pi], y=[dist], c='r', s=20)
    
