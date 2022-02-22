# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 13:54:20 2022

@author: tvdrb
"""


import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import io


  
class AnalyzeAutofocus:
    def __init__(self, path):
        self.folder = path
        self.image_paths = []
        self.position_paths = []
        self.penaltie_paths = []
        self.focus = None
    
    
    def load_data_from_folder(self, folder_name):
        folder_path = self.folder+'\\'+folder_name
        for filename in os.listdir(folder_path):
            if filename.endswith('.tif'):
                if filename.endswith('um.tif'):
                    focus = filename.rstrip('um.tif').split('_')[2]
                    self.focus = float(focus)+60
                else:
                    self.image_paths.append(folder_path+'\\'+filename)
                    filename = filename.strip('autofocus')
                    filename = filename.rstrip('.tif')
                    self.penaltie_paths.append(folder_path+'\\autofocus_penaltyhistory'+filename+'.npy')
                    self.position_paths.append(folder_path+'\\autofocus_positionhistory'+filename+'.npy')
    
    
    def visualize_localization(self, k):
        if type(k) == int:
            image = io.imread(self.image_paths[k])
            positions = np.load(self.position_paths[k])
            penalties = np.load(self.penaltie_paths[k])
            
            max_idx = np.argmax(penalties[-7::])
            sample = positions[-7::]
            print(sample[max_idx]-60)
            
            plt.figure()
            plt.scatter(positions, penalties, c=np.linspace(0,1,len(positions)), cmap='rainbow', label="f(x)", marker='2')
            ax = plt.gca()
            LL = ax.get_ylim()[0]
            UL = ax.get_ylim()[1]
            plt.vlines(self.focus, LL*0.9, UL*1.1, colors='black', linestyles='--', label='true focus')
            plt.xlabel(r'pipette height (in $\mu$m)'); plt.ylabel(r'Variance of Laplacian (a.u.)')
            plt.ylim([LL,UL])
        elif k == 'all':
            fig,axs = plt.subplots(1,len(self.image_paths))
            for i in range(0,len(self.image_paths)):
                image = io.imread(self.image_paths[i])
                axs[i].matshow(image,cmap='gray')
                axs[i].set(xlabel='x (in pixels)', ylabel='y (in pixels)', xticks=[0,2048], yticks=[0,2048], aspect='equal')
                axs[i].xaxis.set_label_position('top')
        elif type(k) == list:
            fig,axs = plt.subplots(1,len(k))
            i = -1
            for idx in k:
                i += 1
                image = io.imread(self.image_paths[idx])
                axs[i].matshow(image,cmap='gray')
                axs[i].set(xlabel='x (in pixels)', ylabel='y (in pixels)', xticks=[0,2048], yticks=[0,2048], aspect='equal')
                axs[i].xaxis.set_label_position('top')
        else:
            print('k unknown datatype')
    
    
    def analyze_raw_data(self, file_name):
        with open(self.folder+'\\'+file_name, 'r') as csvfile:
            z_algorithm = []
            z_groundtruth = []
            cellflags = []
            for line in csvfile:
                cellflag,date,z_alg,z_true = line.split(';')
                if cellflag == 'True' or cellflag == 'False':
                    z_algorithm.append(float(z_alg))
                    z_groundtruth.append(float(z_true))
                    if cellflag == 'True':
                        cellflags.append(True)
                    else:
                        cellflags.append(False)
        
        z_algorithm = np.array(z_algorithm)
        z_groundtruth = np.array(z_groundtruth)
        
        zbias = np.mean(z_algorithm - z_groundtruth)
        zstd = np.std(z_algorithm - z_groundtruth)
        print('bias +/- s.d. (in z):')
        print('{:.1f}'.format(zbias)+' +/- {:.1f}'.format(zstd))
        
        plt.figure()
        plt.scatter(z_algorithm,z_groundtruth)





if __name__ == "__main__":
    analyzer = AnalyzeAutofocus(path=r'C:\Users\tvdrb\Desktop\Autofocus')
    analyzer.load_data_from_folder('2022-2-8')
    analyzer.visualize_localization([1,3,4,5,8])
    # analyzer.analyze_raw_data('raw data.txt')

