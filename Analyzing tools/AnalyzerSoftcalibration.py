# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 15:33:55 2022

@author: tvdrb
"""


import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import io


  
class AnalyzeSoftcalibration:
    def __init__(self, path):
        self.folder = path
        self.image_paths = []
        self.tip_localizations =[]
    
    
    def load_data_from_folder(self, folder_name):
        for filename in os.listdir(self.folder+'\\'+folder_name):
            if filename.endswith('.tif'):
                self.image_paths.append(self.folder+'\\'+folder_name+'\\'+filename)
                
                x_string,y_string = filename.split('_')[1:3]
                x = float(x_string[1::])
                y = float(y_string[1::])
                self.tip_localizations.append((x,y))
    
    
    def visualize_localization(self, k):
        image = io.imread(self.image_paths[k])
        x = self.tip_localizations[k][0]
        y = self.tip_localizations[k][1]
        print(x)
        print(y)
        
        plt.matshow(image,cmap='gray')
        plt.scatter(x, y, color='b', marker='x')
        plt.xticks([0, 2048])
        plt.yticks([0, 2048])
        plt.xlabel('x (in pixels)'); plt.ylabel('y (in pixels)')
        ax = plt.gca()
        ax.set_aspect('equal')
        ax.xaxis.set_label_position('top') 
    
    
    def analyze_raw_data(self, file_name):
        with open(self.folder+'\\'+file_name, 'r') as csvfile:
            x_algorithm = []
            y_algorithm = []
            x_groundtruth = []
            y_groundtruth = []
            cellflags = []
            for line in csvfile:
                cellflag,date,x_alg,y_alg,x_true,y_true = line.split(';')
                if cellflag == 'True' or cellflag == 'False':
                    x_algorithm.append(float(x_alg))
                    y_algorithm.append(float(y_alg))
                    x_groundtruth.append(float(x_true))
                    y_groundtruth.append(float(y_true))
                    if cellflag == 'True':
                        cellflags.append(True)
                    else:
                        cellflags.append(False)
        
        x_algorithm = np.array(x_algorithm)
        y_algorithm = np.array(y_algorithm)
        x_groundtruth = np.array(x_groundtruth)
        y_groundtruth = np.array(y_groundtruth)
        
        xbias = np.mean(x_algorithm - x_groundtruth)
        ybias = np.mean(y_algorithm - y_groundtruth)
        xstd = np.std(x_algorithm - x_groundtruth)
        ystd = np.std(y_algorithm - y_groundtruth)
        print('bias +/- std (in x):')
        print('{:.1f}'.format(xbias)+' +/- {:.1f}'.format(xstd))
        print('bias +/- std (in y):')
        print('{:.1f}'.format(ybias)+' +/- {:.1f}'.format(ystd))        
        
        dx = x_algorithm-x_groundtruth
        dy = y_algorithm-y_groundtruth
        for i in range(0,len(cellflags)):
            if cellflags[i]:
                plt.scatter(dx[i], dy[i], color='b', marker='x')
            else:
                plt.scatter(dx[i], dy[i], color='r', marker='o')
        ax = plt.gca()
        L = max(ax.get_xlim()[0], ax.get_xlim()[1], ax.get_ylim()[0], ax.get_ylim()[1])
        L = 150
        plt.xlim([-L,L]); plt.ylim([-L,L])
        ax.set_aspect('equal')
        plt.grid()
        plt.xlabel('Δx (in pixels)'); plt.ylabel('Δy (in pixels)')
        ax.xaxis.set_label_position('top')
        ax.xaxis.set_ticks_position('top')
        
        plt.scatter([], [], color='b', marker='x', label='with cells')
        plt.scatter([], [], color='r', marker='o', label='without cells')
        plt.legend()




if __name__ == "__main__":
    analyzer = AnalyzeSoftcalibration(path=r'C:\Users\tvdrb\Desktop\Softcalibration')
    # analyzer.load_data_from_folder('2021-12-17')
    # analyzer.visualize_localization(1)
    analyzer.analyze_raw_data('raw data.txt')



