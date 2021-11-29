# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:55:11 2021

@author: tvdrb
"""


import numpy as np
import matplotlib.pyplot as plt

savedirectory = r"C:/Users/tvdrb/Documents/GitHub/Python_test_TF2/PatchClamp/feedback/"

PS1 = np.load(savedirectory+"pressure_recording_sensor1.npy")
PS2 = np.load(savedirectory+"pressure_recording_sensor2.npy")
T = np.load(savedirectory+"pressure_recording_timing.npy")

samplingrate = len(T)/(T[-1] - T[0])

plt.plot(T,PS1)
plt.plot(T,PS2)
plt.legend(['sensor 1', 'sensor 2'])
plt.title('Pressure recording at ' + str(round(samplingrate,2)) + ' samples/second')
plt.xlabel('time (s)')
plt.ylabel('pressure (mBar)')