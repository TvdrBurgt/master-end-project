# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 14:11:17 2021

@author: tvdrb
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io, filters

# =============================================================================
# Automatic pipette focus v2
# =============================================================================

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


def varianceOfLaplacian(img):
    """
    This functions calculates a penalty score that is minimum for sharp images.
    """
    # average images
    img_average = filters.gaussian(img, 4)
    
    # calculate laplacian
    img_laplace = filters.laplace(img_average, 3)
    
    # calculate variance
    penalty = np.var(img_laplace)
    
    return penalty


def outoffocusPenalty(img):
    """
    This function iterates over all images in the Z stack and calculates the
    out-of-focus penalty per image.
    """
    # get Z-stack dimensions
    depth, height, width = img.shape
    
    # constructing Gaussian kernel
    kernel = makeGaussian(width, fwhm=width/8)
    
    print("Calculating penalties...")
    variance = np.empty(depth)
    for idx in range(depth):
        IK = img[idx] * kernel
        variance[idx] = varianceOfLaplacian(IK)
        print(variance[idx])
        if idx == 0:
            plt.imshow(IK)
    
    return variance

#%% 
# load tiff
filepath_2021_03_03 = r"C:\Users\tvdrb\Desktop\Thijs\Z stack\Z stack 2021-03-03.tif"
filepath_2021_03_18 = r"C:\Users\tvdrb\Desktop\Thijs\Z stack\Z stack 2021-03-18.tif"
filepath_2021_03_23 = r"C:\Users\tvdrb\Desktop\Thijs\Z stack\Z stack 2021-03-23.tif"

# calculate out-of-focus penalty for every Z stack
variance_2021_03_03 = outoffocusPenalty(io.imread(filepath_2021_03_03))
variance_2021_03_18 = outoffocusPenalty(io.imread(filepath_2021_03_18))
variance_2021_03_23 = outoffocusPenalty(io.imread(filepath_2021_03_23))

# manually saved z positions
# Translate in Z, #24 corresponds to z=0
zpos_2021_03_03 = np.concatenate([np.arange(-350, -250, 50),
                                  np.arange(-250, -100, 25),
                                  np.arange(-100, -50, 10),
                                  np.arange(-50, -10.001, 5),
                                  np.arange(0, 5.001, 1),
                                  np.arange(5, 100, 10),
                                  np.arange(100, 500, 50),
                                  np.arange(500, 1000, 100),
                                  np.arange(1000, 2000, 250),
                                  np.arange(2000, 3000.001, 500)])
# Z stack 2021-03-18, #85 corresponds to z=0
zpos_2021_03_18 = np.concatenate([np.arange(-300, -250, 50),
                                  np.arange(-250, -100, 25),
                                  np.arange(-100, -50, 10),
                                  np.arange(-50, -3, 1),
                                  np.arange(-3, -2.5, 0.5),
                                  np.arange(-2.5, 5, 0.1),
                                  np.arange(5, 50, 1),
                                  np.arange(50, 100, 10),
                                  np.arange(100, 250, 25),
                                  np.arange(250, 500, 50),
                                  np.arange(500, 2000.001, 100)])
# Z stack 2021-03-23, #13 corresponds to z=0
zpos_2021_03_23 = np.concatenate([np.arange(-30, -10, 10),
                                  np.arange(-10, 0.001, 1),
                                  np.arange(0, 10, 1),
                                  np.arange(10, 100, 10),
                                  np.arange(100, 200.001, 100)])

# Remove badly saved image
zpos_2021_03_18=np.delete(zpos_2021_03_18,181)
variance_2021_03_18=np.delete(variance_2021_03_18,181)


# plot figures
plt.figure()
plt.plot(zpos_2021_03_03, variance_2021_03_03, label='Autofocus 2021/03/03')
plt.plot(zpos_2021_03_18, variance_2021_03_18, label='Autofocus 2021/03/18')
plt.plot(zpos_2021_03_23, variance_2021_03_23, label='Autofocus 2021/03/23')
plt.title('Autofocus scores')
plt.xlabel(r'Focus depth (in $\mu$m)')
plt.ylabel(r'Variance of Laplacian (a.u.)')
plt.legend()
plt.show()

plt.figure()
plt.plot(zpos_2021_03_03, variance_2021_03_03/max(variance_2021_03_03), label='Autofocus 2021/03/03 (normalized)')
plt.plot(zpos_2021_03_18, variance_2021_03_18/max(variance_2021_03_18), label='Autofocus 2021/03/18 (normalized)')
plt.plot(zpos_2021_03_23, variance_2021_03_23/max(variance_2021_03_23), label='Autofocus 2021/03/23 (normalized)')
plt.title('Autofocus scores (normalized)')
plt.xlabel(r'Focus depth (in $\mu$m)')
plt.ylabel(r'Variance of Laplacian (a.u.)')
plt.legend()
plt.show()

plt.figure()
plt.plot(zpos_2021_03_18[0:-1], np.diff(variance_2021_03_18), label='Autofocus 2021/03/18 (normalized)')


#%% 

import numpy as np
import matplotlib.pyplot as plt

historydatapath = r'W:\staff-groups\tnw\ist\do\projects\Neurophotonics\Brinkslab\Data\Thijs\run 7 exposure 0.01'

position = np.load(historydatapath + "\\positionhistory.txt.npy")
penalties = np.load(historydatapath + "\\penaltyhistory.txt.npy")
# position = np.loadtxt(historydatapath + "\\positionhistory.txt")
# penalties = np.loadtxt(historydatapath + "\\penaltyhistory.txt")

# plot penalty graph
plt.figure()
plt.scatter(position/100, penalties, c=np.linspace(0,1,len(position)), cmap='rainbow')
plt.title('Sharpness function (Exposure time x0.05)')
plt.xlabel(r'Focus depth (in $\mu$m)')
plt.ylabel(r'Variance of Laplacian (a.u.)')
cbar = plt.colorbar(ticks=[0,1])
cbar.ax.set_yticklabels(['first step','last step'])
plt.show()



