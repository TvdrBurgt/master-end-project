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
filepath = r"C:\Users\tvdrb\Desktop\NB5900 Research Project\Pipette tips\boyden.png"
I = io.imread(filepath)

# Convert Tiff to 2D if Z-stack is the same
I = I[:,:,0]
        

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
    Rpar = R[np.where(cutoff >= np.sqrt(2)/2)]
    Tperp = T[np.where(cutoff < np.sqrt(2)/2)]
    Rperp = R[np.where(cutoff < np.sqrt(2)/2)]
    
    # determine a and b in y=ax+b (parallel)
    a = np.tan(np.pi/2+Tpar)
    b = Rpar/np.sin(Tpar)
    # determine c and d in x=cy+d (perpundicular)
    c = np.tan(-Tperp)
    d = Rperp/np.cos(Tperp)
    
    # prevent dividing by zero in the next step
    a[a==0] = 1e-9
    c[c==0] = 1e-9
    
    # determine crossings with the lines: y=0, x=0, y=height, x=width (parallel)
    x0 = -b/a
    y0 = b
    xh = (height-b)/a
    yw = a*width + b
    # determine crossings with the lines: y=0, x=0, y=height, x=width (perpundicular)
    x_0 = d
    y_0 = -d/c
    x_h = c*height + d
    y_w = (width-d)/c
    
    # place crossings on the image edge (parallel)
    x0[x0>width-1] = width-1
    x0[x0<0] = 0
    y0[y0>height-1] = height-1
    y0[y0<0] = 0
    xh[xh>width-1] = width-1
    xh[xh<0] = 0
    yw[yw>height-1] = height-1
    yw[yw<0] = 0
    # place crossings on the image edge (perpundicular)
    x_0[x_0>width-1] = width-1
    x_0[x_0<0] = 0
    y_0[y_0>height-1] = height-1
    y_0[y_0<0] = 0
    x_h[x_h>width-1] = width-1
    x_h[x_h<0] = 0
    y_w[y_w>height-1] = height-1
    y_w[y_w<0] = 0
    
    # match coordinates (parallel)
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
    # match coordinates (perpundicular)
    x_left = np.zeros((len(Tperp)))
    y_left = np.zeros((len(Tperp)))
    x_right = np.zeros((len(Tperp)))
    y_right = np.zeros((len(Tperp)))
    for i in range(len(Tperp)):
        x_left[i] = np.min([x_0[i],x_h[i]])
        x_right[i] = np.max([x_0[i],x_h[i]])
        if c[i] > 0:
            y_left[i] = np.min([y_0[i],y_w[i]])
            y_right[i] = np.max([y_0[i],y_w[i]])
        else:
            y_left[i] = np.max([y_0[i],y_w[i]])
            y_right[i] = np.min([y_0[i],y_w[i]])
            
    # let x and y be rows and columns (parallel)
    c0 = np.around(xleft).astype(int)
    r0 = np.around(yleft).astype(int)
    c1 = np.around(xright).astype(int)
    r1 = np.around(yright).astype(int)
    # let x and y be rows and columns (perpundicular)
    c_0 = np.around(x_left).astype(int)
    r_0 = np.around(y_left).astype(int)
    c_1 = np.around(x_right).astype(int)
    r_1 = np.around(y_right).astype(int)
    
    # append coordinates from parallel and perpundicular lines
    C0 = np.append(c0,c_0)
    R0 = np.append(r0,r_0)
    CW = np.append(c1,c_1)
    RH = np.append(r1,r_1)
    
    return R0, C0, RH, CW

# Gaussian blur
print('Gaussian blurring...\n')
IB = filters.gaussian(I, 15)

# Canny edge detection
print('Canny edge detection...\n')
BW = feature.canny(IB, sigma=10, low_threshold=0.9, high_threshold=0.7, use_quantiles=True)

# Hough transform
print('Calculating Hough transform...\n')
# H, T, R = transform.hough_line(BW,np.linspace(np.pi/3,2*np.pi/3,120*100))
H, T, R = transform.hough_line(BW,np.linspace(2*np.pi/12,5*np.pi/12,120*100))

# extract most common lines in the image from the Hough transform
print('Finding most common lines from Hough transform...\n')
num_lines = 17
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
canvasblur = filters.gaussian(canvas, 5)

# extract pipette tip
ypos, xpos = np.where(canvasblur == np.max(canvasblur))
xpos = xpos[-1]; ypos = ypos[-1]
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
    
