# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 14:00:10 2022

@author: tvdrb
"""


import os
import numpy as np
import matplotlib.pyplot as plt


  
class AnalyzeGigaseal:
    def __init__(self, path):
        self.folder = path
        self.resistances = []
        self.timestep = 20  #ms
    
    
    def load_data_from_folder(self, folder_name):
        folder_path = self.folder+'\\'+folder_name
        for filename in os.listdir(folder_path):
            if filename.endswith('.npy') and filename.startswith('gigaseal_'):
                resistance_history = np.load(folder_path+'\\'+filename)
                self.resistances.append(resistance_history)
    
    
    def visualize_resistance(self, k):
        if type(k) == int:
            resistance_history = self.resistances[k]
            time = np.linspace(0,len(resistance_history)*20/1000,len(resistance_history))
            plt.scatter(time, resistance_history/1e6, marker='.', color='black')
            plt.xlabel('time (in s)'); plt.ylabel('Resistance (in MΩ)')
        elif k == 'all':
            plt.figure()
            for i in range(0,len(self.resistances)):
                time = np.linspace(0, len(self.resistances[i])*20/1000, len(self.resistances[i]))
                plt.plot(time, self.resistances[i]/1e6)
                plt.xlabel('time (in s)'); plt.ylabel('Resistance (in MΩ)')
        elif type(k) == list:
            plt.figure()
            for i in k:
                time = np.linspace(0, len(self.resistances[i])*20/1000, len(self.resistances[i]))
                plt.plot(time, self.resistances[i]/1e6)
                plt.xlabel('time (in s)'); plt.ylabel('Resistance (in MΩ)')
        else:
            print('k unknown datatype')





if __name__ == "__main__":
    analyzer = AnalyzeGigaseal(path=r'C:\Users\tvdrb\Desktop\Gigaseal')
    analyzer.load_data_from_folder('2022-2-11')
    analyzer.visualize_resistance(10)

