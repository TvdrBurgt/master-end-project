# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:17:08 2021

@author: tvdrb
"""

import numpy as np
from skimage import io, filters, feature, transform
import matplotlib.pyplot as plt


# =============================================================================
# Pipette Recognition
# =============================================================================

# load tiff
filepath = r"C:\Users\tvdrb\Desktop\Thijs\XY grid\grid 150 -100 0.tif"
I = io.imread(filepath)

######################### parameter settings #########################
# physical parameters
upper_angle = 97.5  # guess upper angle of pipette (in degree)
lower_angle = 82.5  # guess lower angle of pipette (in degree)
diameter = 16.5     # pipette tip diameter (in pixels)

######################################################################


def plotCoord(I,angle1,dist1,angle2,dist2,xpos,ypos):
    fig, axs = plt.subplots(1,2)
    # subplot with Houghlines
    axs[0].matshow(I, cmap='gray'); axs[0].axis('image')
    (x1, y1) = dist1*np.array([np.cos(angle1), np.sin(angle1)])
    (x2, y2) = dist2*np.array([np.cos(angle2), np.sin(angle2)])
    axs[0].axline((x1 ,y1), slope=np.tan(angle1 + np.pi/2), c='r')
    axs[0].axline((x2 ,y2), slope=np.tan(angle2 + np.pi/2), c='g')
    # subplot with tip coordinates
    axs[1].matshow(I, cmap='gray'); axs[1].axis('image')
    axs[1].scatter(x=xpos, y=ypos, c='r', s=30)
    axs[1].annotate('(%d,%d)' % (xpos,ypos), (xpos+30, ypos-15), c='r')
    fig.show()
    
def plotBlurCannyHough(IB,BW,Tcommon1,Rcommon1,Tcommon2,Rcommon2):
    fig, axs = plt.subplots(1,3)
    # subplot with original image blurred
    axs[0].matshow(IB, cmap='gray', aspect = 'auto'); axs[0].axis('image'); axs[0].axis('off')
    for angle, dist in zip(Tcommon1,Rcommon1):
        (x, y) = dist*np.array([np.cos(angle), np.sin(angle)])
        axs[0].axline((x ,y), slope=np.tan(angle + np.pi/2), c='r')
    for angle, dist in zip(Tcommon2,Rcommon2):
        (x, y) = dist*np.array([np.cos(angle), np.sin(angle)])
        axs[0].axline((x ,y), slope=np.tan(angle + np.pi/2), c='g')
    # subplot with canny edge detection
    axs[1].matshow(BW, cmap='gray', aspect = 'auto'); axs[1].axis('image'); axs[1].axis('off')
    # subplot with Houghspace
    left_theta = min(min(Tcommon1),min(Tcommon2))
    right_theta = max(max(Tcommon1),max(Tcommon2))
    H, T, R = transform.hough_line(BW,np.linspace(left_theta,right_theta,10000))
    axs[2].imshow(np.log(1+H), extent=[np.rad2deg(T[0]), np.rad2deg(T[-1]), R[-1], R[0]], aspect='auto')
    axs[2].set_xlabel(r'$\theta$ (degree)')
    axs[2].set_ylabel(r'$\rho$ (pixels)')
    for angle, dist in zip(Tcommon1,Rcommon1):
        axs[2].scatter(x=[np.rad2deg(angle)], y=[dist], c='r', s=20)
    for angle, dist in zip(Tcommon2,Rcommon2):
        axs[2].scatter(x=[np.rad2deg(angle)], y=[dist], c='g', s=20)
    fig.show()
    

def detectPipettetip(I, upper_angle, lower_angle, diameter, blursize=15, 
                     angle_range=10, num_angles=5000, num_peaks=8, plotflag=True):
    """ 
    Tip detection algorithm 
    software parameters:
    blursize    = kernel size for gaussian blur
    angle_range = angle search range (in degree)
    num_angles  = number of sampling angles in Hough transform
    num_peaks   = number of peaks to find in Hough space
    plotflag    = if True it will generate figures
    """
    
    # Gaussian blur
    print('I)\t Gaussian blurring...')
    IB = filters.gaussian(I, blursize)
    
    # Canny edge detection
    print('II)\t Canny edge detection...')
    BW = feature.canny(IB, sigma=10, low_threshold=0.98, high_threshold=0.7, use_quantiles=True)
    
    # Double-sided Hough transform
    print('III) Calculating Hough transform...')
    if np.abs(upper_angle-lower_angle) < angle_range:
        theta1 = upper_angle + np.linspace(angle_range/2, -np.abs(upper_angle-lower_angle)/2, num_angles)
        theta2 = lower_angle + np.linspace(np.abs(upper_angle-lower_angle)/2, -angle_range/2, num_angles)
    else:
        theta1 = upper_angle + np.linspace(angle_range/2, -angle_range/2, num_angles)
        theta2 = lower_angle + np.linspace(angle_range/2, -angle_range/2, num_angles)
    # append theta's and transform to radians
    theta = np.deg2rad(np.append(theta1,theta2))
    # calculate Hough transform
    H, T, R = transform.hough_line(BW,theta)
    # split Hough transform in two because of two angles
    H1, H2 = np.hsplit(H,2)
    T1, T2 = np.hsplit(T,2)
    
    # extract most common lines in the image from the double-sided Hough transform
    print('IV)\t Finding most common lines from Hough transform...')
    _, Tcommon1, Rcommon1 = transform.hough_line_peaks(H1,T1,R,num_peaks=num_peaks,threshold=0)
    _, Tcommon2, Rcommon2 = transform.hough_line_peaks(H2,T2,R,num_peaks=num_peaks,threshold=0)
    # find the average value so we end up with two lines
    angle1 = np.mean(Tcommon1)
    dist1 = np.mean(Rcommon1)
    angle2 = np.mean(Tcommon2)
    dist2 = np.mean(Rcommon2)
    
    # find intersection between X1*cos(T1)+Y1*sin(T1)=R1 and X2*cos(T2)+Y2*sin(T2)=R2
    print('V)\t Calculating preliminary pipette point...')
    LHS = np.array([[np.cos(angle1), np.sin(angle1)], [np.cos(angle2), np.sin(angle2)]])
    RHS = np.array([dist1, dist2])
    xpos, ypos = np.linalg.solve(LHS, RHS)
    
    # account for xposition overestimation bias
    print('VI)\t Correcting for pipette diameter...')
    deltax = (diameter/2)/np.sin(np.abs(angle1-angle2)/2)
    deltay = (diameter/2)*np.cos((angle1+angle2)/2)
    xpos = xpos - deltax
    ypos = ypos + deltay
    print(deltay)
    
    # plot figures if plotflag is True
    if plotflag:
        plotCoord(I,angle1,dist1,angle2,dist2,xpos,ypos)
        plotBlurCannyHough(IB,BW,Tcommon1,Rcommon1,Tcommon2,Rcommon2)
    
    return xpos, ypos
    


if __name__ == '__main__':
    detectPipettetip(I, upper_angle, lower_angle, diameter, plotflag=True)
    