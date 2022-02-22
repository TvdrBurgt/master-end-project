# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:55:11 2021

@author: tvdrb
"""


import numpy as np
import matplotlib.pyplot as plt

savedirectory = r"W:/staff-groups/tnw/ist/do/projects/Neurophotonics/Brinkslab\Data/Thijs/Break-in pressure Xin/"

PS1 = np.load(savedirectory+"pressure_recording_sensor1.npy")
PS2 = np.load(savedirectory+"pressure_recording_sensor2.npy")
T = np.load(savedirectory+"pressure_recording_timing.npy")

samplingrate = len(T)/(T[-1] - T[0])


plt.figure(2)
T = T[565::]-10
PS1 = PS1[565::]
plt.plot(T,PS1)
plt.title('Pressure recording @ ' + str(round(samplingrate,2)) + 'Hz')
plt.xlabel('time (s)')
plt.ylabel('pressure (mBar)')

datapoints_in_peaks = len(T[np.where(PS1<-5)])
n_peaks = 18
peak_duration = datapoints_in_peaks/n_peaks/samplingrate
print("Average pulse duration: {}".format(peak_duration))
