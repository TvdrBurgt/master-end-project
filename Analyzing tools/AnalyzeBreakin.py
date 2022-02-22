# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 14:32:31 2022

@author: tvdrb
"""


import os
import numpy as np
import matplotlib.pyplot as plt


  
class AnalyzeBreakin:
    def __init__(self, path):
        self.folder = path
        self.resistances = []
        self.currents_max = []
        self.currents_min = []
        self.currentwindow = []
        self.timestep = 20  #ms
    
    
    def load_data_from_folder(self, folder_name):
        folder_path = self.folder+'\\'+folder_name
        for filename in os.listdir(folder_path):
            if filename.endswith('.npy') and filename.startswith('breakin_resistance'):
                resistance_history = np.load(folder_path+'\\'+filename)
                self.resistances.append(resistance_history)
            if filename.endswith('.npy') and filename.startswith('breakin_current'):
                Imax,Imin = np.load(folder_path+'\\'+filename)
                self.currents_max.append(Imax)
                self.currents_min.append(Imin)
            if filename.endswith('.npy') and filename.startswith('breakin_slidingwindow'):
                window = np.load(folder_path+'\\'+filename)
                self.currentwindow.append(window)
    
    
    def visualize_breakin(self, k):
        fig,axs = plt.subplots(2,1)
        if type(k) == int:
            resistances = self.resistances[k]
            currents_max = self.currents_max[k]
            currents_min = self.currents_min[k]
            time = np.linspace(0, len(resistances), len(resistances))
            axs[0].plot(time, resistances/1e6, marker='.', color='red')
            axs[0].set(ylabel='Resistance (in MΩ)', xticks=[])
            axs[1].plot(time, currents_max*1e9, linestyle='-.', color='blue')
            axs[1].plot(time, currents_min*1e9, linestyle='-.', color='blue')
            axs[1].set(xlabel='time (in s)', ylabel='Current (in µA)')
            axs[0].set(title='Break-in attempt')
            
            plt.figure()
            time = np.linspace(0, 20, len(self.currentwindow[k]))
            plt.plot(time, self.currentwindow[k]*1e12, color='blue')
            plt.xticks([0,5,10,15,20])
            plt.xlabel('time (in ms)'); plt.ylabel('Current (in pA)')
            plt.title('Sliding window averaged over 200ms')





if __name__ == "__main__":
    analyzer = AnalyzeBreakin(path=r'C:\Users\tvdrb\Desktop\Breakin')
    analyzer.load_data_from_folder('2022-2-11')
    analyzer.visualize_breakin(5)

