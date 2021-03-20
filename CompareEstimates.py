# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 21:09:43 2021

@author: tvdrb
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# =============================================================================
# Tool for quantitatively comparing pipette tip estimates
# =============================================================================

# target folder containing the images to be annotated
path = r'C:\Users\tvdrb\Desktop\Pipette attenuations'

# names of files to compare
groundtruth = "Z stack attenuated - kopie"
estimate = "Z stack algorithm - kopie"

# image size
xsize = 2048
ysize = xsize

# read files
groundtruth = pd.read_csv(path+"\\"+groundtruth, sep=';')
estimate = pd.read_csv(path+"\\"+estimate, sep=';')


# calculate position differences
name = []
x1 = []
x2 = []
y1 = []
y2 = []
dx = []
dy = []
for index, row in groundtruth.iterrows():
    if row[0] == estimate.filename[index]:
        name.append(row[0])
        x1.append(row[1])
        y1.append(row[2])
        x2.append(estimate.x[index]-50)
        y2.append(estimate.y[index])
        dx.append(row[1] - estimate.x[index]-50)
        dy.append(row[2] - estimate.y[index])
    else:
        print("Filename does not correspond:\n{}".format(row[0]))

# create new datafile containing all information
combinedfile = pd.DataFrame(list(zip(name,x1,y1,x2,y2,dx,dy)),
                            columns =['Filename','x1','y1','x2','y2','dx','dy'])


############################ Quantitative analysis ############################
# convert coordinate lists to numpy arrays
x1 = np.array(x1)
x2 = np.array(x2)
y1 = np.array(y1)
y2 = np.array(y2)
dx = np.array(dx)
dy = np.array(dy)

# divide the field of view into segments
num_segments = 4

# create boolean matrix with each column another segment
segmentclass = np.zeros((len(name),num_segments+1), dtype=bool)
centerdistance = np.sqrt((x1-xsize/2)**2 + (y1-ysize/2)**2)

# match coordinates with their corresponding segment
for i in range(num_segments+1):
    lowerbound = ysize/(num_segments)/2*i
    upperbound = ysize/(num_segments)/2*(i+1)
    # check if coordinates fall within a segment
    segmentclass[:,i] = (centerdistance>=lowerbound) & (centerdistance<upperbound)

# calculate mean and standard deviation per segment
errordistance = np.sqrt(dx**2 + dy**2)
print("Segment #: μ ± σ (in pixels)")
mu = np.zeros(num_segments+1)
mu_x = np.zeros(num_segments+1)
mu_y = np.zeros(num_segments+1)
sigma = np.zeros(num_segments+1)
sigma_x = np.zeros(num_segments+1)
sigma_y = np.zeros(num_segments+1)
for i in range(num_segments+1):
    print("Segment %d:" % (i+1))
    # calculate mean per segment
    mu[i] = np.nanmean(errordistance[segmentclass[:,i]])
    mu_x[i] = np.nanmean(dx[segmentclass[:,i]])
    mu_y[i] = np.nanmean(dy[segmentclass[:,i]])
    # calculate standard deviation per segment
    sigma[i] = np.nanstd(errordistance[segmentclass[:,i]])
    sigma_x[i] = np.nanstd(dx[segmentclass[:,i]])
    sigma_y[i] = np.nanstd(dy[segmentclass[:,i]])
    print("\t in x: %.2f +/- %.2f" % (mu_x[i],sigma_x[i]))
    print("\t in y: %.2f +/- %.2f" % (mu_y[i],sigma_y[i]))
    print("\t total: %.2f +/- %.2f" % (mu[i],sigma[i]))

########################## Construct Figure Segments ##########################

fig, axs = plt.subplots(1,2)
axs[0].hist(dx[~np.isnan(dx)], bins=500)
axs[0].set_title('X bias')
axs[0].set_xlabel(r'Bias (in $\mu$m)')
axs[0].set_ylabel('Count')
axs[1].hist(dy[~np.isnan(dy)], bins=500)
axs[1].set_title('Y bias')
axs[1].set_xlabel(r'Bias (in $\mu$m)')
axs[1].set_ylabel('Count')

########################## Construct Figure Segments ##########################
fig,ax = plt.subplots()

# set figure properties
ax.set_title('Localization precision: MEAN +/- SD')
ax.set_xlabel('x (in pixels)'); ax.set_ylabel('y (in pixels)')
ax.set_xlim([0, xsize]); ax.set_ylim([ysize, 0])
ax.set_aspect('equal')

# plot segments as circles around the image center
c = cm.rainbow(np.linspace(0, 1, num_segments+1))
legend_items = []
for i in range(num_segments+1):
    r = ysize/(num_segments)/2*(i+1)
    ax.add_patch(plt.Circle((xsize/2, ysize/2), radius=r, linestyle=':', color=c[i], fill=False))
    legend_items += [plt.scatter([], [], marker='.', color=c[i], label=('%f+/-%f'%(mu[i],sigma[i])))]

# add custom legend
plt.legend(handles=legend_items)

# show plot
plt.show()


############################ Construct Figure Grid ############################
plt.figure()

# set figure properties
plt.title('Pipette tip localization comparison')
plt.xlabel('x (in pixels)'); plt.ylabel('y (in pixels)')
plt.xlim([0, xsize]); plt.ylim([ysize, 0])

# make scatter plot
colors = cm.rainbow(np.linspace(0, 1, len(name)))
for i in range(len(name)):
    plt.scatter(x1[i], y1[i], color=colors[i,:], marker='x')
    plt.scatter(x2[i], y2[i], color=colors[i,:], marker='o')

# add custom legend
legend_elements = [plt.scatter([], [], marker='x', color='black', label='Ground truth'),
                   plt.scatter([], [], marker='o', color='black', label='Algorithm')]
plt.legend(handles=legend_elements)

# show plot
plt.show()


