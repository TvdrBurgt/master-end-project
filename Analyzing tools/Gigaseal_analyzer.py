# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 21:21:55 2021

@author: tvdrb
"""


import numpy as np
import matplotlib.pyplot as plt

path = r'C:\Users\tvdrb\Desktop'

gigasealtimestamp = r'gigaseal_2021-12-02_20-04-12'

resistances = np.load(path + "\\" + gigasealtimestamp[0:8] + "_resistancehistory_" + gigasealtimestamp[9::] + ".npy")
# snapshot = plt.imread(path + "\\" + gigasealtimestamp + ".tif")

# plot resistance graph
plt.figure()
plt.title('Resistance')
plt.plot(resistances/1e6)
plt.xlabel(r'Time (a.u.)')
plt.ylabel(r'Resistance (in MOhm)')

# plt.matshow(snapshot, cmap='gray')
