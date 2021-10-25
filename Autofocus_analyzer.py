# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 09:34:23 2021

@author: tvdrb
"""

import numpy as np
import matplotlib.pyplot as plt

path = r'C:\Users\tvdrb\Desktop\Test runs\feedback 1'

penalties = np.load(path + "\\autofocus_penaltyhistory.npy")
positions = np.load(path + "\\autofocus_positionhistory.npy")
positions -= 722


# first derivative (central difference)
df = []
ddf = []
argpos = []
for i in range(1,len(positions)-1):
    h_m = abs(positions[i] - positions[i-1])
    h_p = abs(positions[i] - positions[i+1])
    if i < len(positions)-2:
        h_pp = abs(positions[i+2] - positions[i])
    else: h_pp = 0
    
    if h_m == h_p:
        df.append( (penalties[i+1] - penalties[i-1]) / 2*h_m)
        ddf.append( (penalties[i+1] - 2*penalties[i] + penalties[i-1]) / h_m**2)
        argpos.append(i)
    elif h_p == h_pp:
        df.append( (penalties[i+2] - penalties[i+1]) / h_p)
        ddf.append( (penalties[i+2] - 2*penalties[i] + penalties[i+1]) / h_p**2)
        argpos.append(i)
    else:
        print('skipped')
df = np.array(df)
ddf = np.array(ddf)
argpos = np.array(argpos)


# plot penalty graph
plt.figure()
plt.title('Sharpness function')
plt.scatter(positions/100, penalties, c=np.linspace(0,1,len(positions)), cmap='rainbow', label="f(x)", marker='2')
plt.xlabel(r'Focus depth (in $\mu$m)')
plt.ylabel(r'Variance of Laplacian (a.u.)')

df_negative = np.where(df<0)
ddf_negative = np.where(ddf<0)

fig, (ax1,ax2) = plt.subplots(2, sharex=True)
ax2.plot(positions[argpos]/100, df, label="f'(x)", color='orange')
ax2.plot(positions[argpos]/100, ddf, label="f''(x)", color='green')
ax2.scatter(positions[argpos][df_negative]/100, df[df_negative], color='orange', marker='o')
ax2.scatter(positions[argpos][ddf_negative]/100, ddf[ddf_negative], color='green', marker='x')
fig.suptitle("Focus penalties and derivatives")
ax1.plot(positions/100, penalties, label="f(x)")
ax2.set(xlabel=r'Focus depth (in $\mu$m)', ylabel=r'Variance of Laplacian (a.u.)')
ax2.legend()