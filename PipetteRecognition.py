# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:17:08 2021

@author: tvdrb
"""

import numpy as np
from skimage import io, filters, feature, transform
from scipy import cluster
import matplotlib.pyplot as plt

# =============================================================================
# Pipette Recognition
# =============================================================================

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

def plotBlurCannyHough(IB,BW,Tpeaks,Rpeaks,centroids,labels):
    fig, axs = plt.subplots(1,3)
    # subplot with original image blurred
    axs[0].matshow(IB, cmap='gray', aspect = 'auto'); axs[0].axis('image'); axs[0].axis('off')
    for angle, dist in zip(Tpeaks,Rpeaks):
        (x, y) = dist*np.array([np.cos(angle), np.sin(angle)])
        axs[0].axline((x ,y), slope=np.tan(angle + np.pi/2), c='r')
    # subplot with canny edge detection
    axs[1].matshow(BW, cmap='gray', aspect = 'auto'); axs[1].axis('image'); axs[1].axis('off')
    # subplot with Houghspace
    H, T, R = transform.hough_line(BW,np.linspace(0,3*np.pi,1500))
    axs[2].imshow(np.log(1+H), extent=[np.rad2deg(T[0]), np.rad2deg(T[-1]), R[-1], R[0]], aspect='auto')
    axs[2].set_xlabel(r'$\theta$ (degree)')
    axs[2].set_ylabel(r'$\rho$ (pixels)')
    for angle, dist, label in zip(Tpeaks,Rpeaks,labels):
        if label == 0:
            color = 'r'
        else:
            color = 'g'
        axs[2].scatter(x=[np.rad2deg(angle)], y=[dist], c=color, s=20, marker='.')
    for angle, dist, color in zip(centroids[:,0], centroids[:,1], ['r','g']):
        axs[2].scatter(x=[np.rad2deg(angle)], y=[dist], c=color, s=40, marker='x')
    fig.show()


def makeGaussian(size=(2048,2048), mu=(1024,1024), sigma=(512,512)):
        """
        This function returns a normalized Gaussian distribution in 2D with a
        user specified center position and standarddeviation.
        """
        
        x = np.arange(0, size[0], 1, float)
        y = np.arange(0, size[1], 1, float)
        
        gauss = lambda x,mu,sigma: np.exp((-(x-mu)**2)/(2*sigma**2))
        
        xs = gauss(x, mu[0], sigma[0])
        ys = gauss(y, mu[1], sigma[1])
        
        xgrid = np.tile(xs, (size[1],1))
        ygrid = np.tile(ys, (size[0],1)).transpose()
        
        window = np.multiply(xgrid,ygrid)
        
        return window/np.sum(window)


def detectPipettetip(Ia, Ib, diameter, orientation, plotflag=False):
    """ 
    Tip detection algorithm 
    input parameters:
        Ia          = previous image of pipette tip
        Ib          = current image of pipette tip
        diameter    = diameter of pipette tip in pixels
        orientation = pipette orientation in degree, clockwise calculated from
                      the horizontal pointing to the right (= 0 degree)
        plotflag    = if True it will generate figures
    output parameters:
        xpos        = x position of the pipette tip
        ypos        = y position of the pipette tip
    """
    
    # Gaussian blur
    print('I)')
    LB = filters.gaussian(Ia, 1)
    RB = filters.gaussian(Ib, 1)
    
    # Image subtraction
    print('II)')
    IB = LB - RB
    
    # Canny edge detection
    print('III)')
    BW = feature.canny(IB, sigma=3, low_threshold=0.99, high_threshold=0, use_quantiles=True)
    
    # Hough transform
    print('IV)')
    angle_range = np.linspace(0, np.pi, 500) + np.deg2rad(orientation)
    H, T, R = transform.hough_line(BW, angle_range)
    
    # Find Hough peaks
    print('V)')
    _, Tpeaks, Rpeaks = transform.hough_line_peaks(H,T,R, num_peaks=5, threshold=0)
    
    # Cluster peaks
    print('VI)')
    idx_lowT = np.argmin(Tpeaks)
    idx_highT = np.argmax(Tpeaks)
    initial_clusters = np.array([[Tpeaks[idx_lowT],Rpeaks[idx_lowT]], [Tpeaks[idx_highT],Rpeaks[idx_highT]]])
    data = np.transpose(np.vstack([Tpeaks,Rpeaks]))
    centroids, labels = cluster.vq.kmeans2(data, k=initial_clusters, iter=10, minit='matrix')
    centroid1, centroid2 = centroids
    
    
    # Find intersection between X1*cos(T1)+Y1*sin(T1)=R1 and X2*cos(T2)+Y2*sin(T2)=R2
    print('VII)')
    if centroid1[0] > centroid2[0]:
        angle1,dist1 = centroid1
        angle2,dist2 = centroid2
    else:
        angle1,dist1 = centroid2
        angle2,dist2 = centroid1
    LHS = np.array([[np.cos(angle1), np.sin(angle1)], [np.cos(angle2), np.sin(angle2)]])
    RHS = np.array([dist1, dist2])
    xpos, ypos = np.linalg.solve(LHS, RHS)
    
    # Bias correction
    print('VIII)')
    H = diameter/(2*np.tan((angle1-angle2)/2))
    alpha = (angle1+angle2)/2 - np.pi/2
    xpos = xpos - H*np.cos(alpha)
    ypos = ypos - H*np.sin(alpha)
    
    # plot figures if plotflag is True
    if plotflag:
        plotCoord(Ib,angle1,dist1,angle2,dist2,xpos,ypos)
        plotBlurCannyHough(IB,BW,Tpeaks,Rpeaks,centroids,labels)
    
    return xpos, ypos
    
    
if __name__ == '__main__':
    Ia = io.imread(r"C:\Users\tvdrb\Desktop\2021-08-16\X250Y250a.tif")
    Ib = io.imread(r"C:\Users\tvdrb\Desktop\2021-08-16\X250Y250b.tif")
    
    x1, y1 = detectPipettetip(Ia, Ib, diameter=16, orientation=0)
    
    W = makeGaussian(size=Ia.shape, mu=(x1,y1), sigma=(Ia.shape[0]//12,Ia.shape[1]//12))
    IaW = np.multiply(Ia,W)
    IbW = np.multiply(Ib,W)
    
    x,y = detectPipettetip(IaW, IbW, diameter=20, orientation=0, plotflag=True)
    