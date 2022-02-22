# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 09:50:10 2022

@author: tvdrb
"""


import os
import numpy as np


  
class AnalyzeHardcalibration:
    def __init__(self, path):
        self.folder = path
        self.stepsize = None
        self.positionsXY = []
        self.positionsXYZ = []
        self.positionspixelsize = []
        self.gamma = []
        self.pixelsize = []
    
    @property
    def R(self):
        return self._R
    @R.setter
    def R(self, alphabetagamma):
        alpha,beta,gamma = alphabetagamma
        R_alpha = np.array([[1, 0, 0],
                            [0, np.cos(alpha), np.sin(alpha)],
                            [0, -np.sin(alpha), np.cos(alpha)]])
        R_beta = np.array([[np.cos(beta), 0, -np.sin(beta)],
                           [0, 1, 0],
                           [np.sin(beta), 0, np.cos(beta)]])
        R_gamma = np.array([[np.cos(gamma), np.sin(gamma), 0],
                            [-np.sin(gamma), np.cos(gamma), 0],
                            [0, 0, 1]])
        try:
            self._R = self._R @ R_gamma @ R_beta @ R_alpha
        except AttributeError:
            self._R = R_gamma @ R_beta @ R_alpha
    @R.deleter
    def R(self):
        self._R = np.eye(3)
    
    def account4rotation(self, origin, target):
        if isinstance(origin, np.ndarray) and isinstance(target, np.ndarray):
            if origin.shape == (3,) and target.shape == (3,):
                pass
            else:
                raise ValueError('origin and target should have shape (3,)')
        else:
            raise ValueError('origin and target should be numpy.ndarray')
        
        return self.R @ np.subtract(target,origin) + origin
    
    
    def set_constants(self, gamma, stepsize):
        self.stepsize = stepsize
        self.R = (0,0,gamma)
    
    
    def load_data_from_folder(self):
        for filename in os.listdir(self.folder):
            if filename.startswith('hardcalibrationXY_'):
                arr = np.load(self.folder+'\\'+filename)
                self.positionsXY.append(arr)
            elif filename.startswith('hardcalibrationXYZ_'):
                arr = np.load(self.folder+'\\'+filename)
                self.positionsXYZ.append(arr)
            elif filename.startswith('hardcalibrationpixelsize_'):
                arr = np.load(self.folder+'\\'+filename)
                self.positionspixelsize.append(arr)
            else:
                print('filename not recognized')
    
    
    def analyze_XY(self):
        for tipcoords in self.positionsXY:
            # reduce tip coordinates to a unit step mean deviation
            tipcoords_diff = np.diff(tipcoords,axis=1)
            E = np.mean(tipcoords_diff,axis=1)/self.stepsize
            
            # calculate rotation angles
            if E[0,0] > 0:
                gamma = np.arctan(-E[0,1]/E[0,0])
            else:
                gamma = np.arctan(-E[0,1]/E[0,0]) - np.pi
            print(gamma)
            self.gamma.append(gamma*180/np.pi)
        
        print('gamma (in degree) bias +/- s.d.: {:.5f}'.format(-np.mean(self.gamma))+' +/- {:.5f}'.format(np.std(self.gamma)))
        
    
    
    def analyze_pixelsize(self):
        for tipcoords in self.positionspixelsize:
            positions = np.linspace(-3*self.stepsize, 3*self.stepsize, num=7)
            reference = np.array([0,0,0])
            
            # get all micromanipulator-pixel pairs in the XY plane
            directions = np.eye(3)
            pixcoords = tipcoords[0:2,:,0:2]
            realcoords = np.tile(np.nan, (2,len(positions),2))
            for i in range(2):
                for j, pos in enumerate(positions):
                    x,y,z = self.account4rotation(origin=reference, target=reference+directions[i]*pos)
                    realcoords[i,j] = np.array([x,y])
            
            # couple micrometer distance with pixeldistance and take the mean
            diff_realcoords = np.abs(np.diff(realcoords, axis=1))   # in microns
            diff_pixcoords = np.abs(np.diff(pixcoords, axis=1))     # in pixels
            samples = diff_realcoords/diff_pixcoords                # microns per pixel
            sample = np.array([samples[0,:,0], samples[1,:,1]])
            pixelsize = np.mean(sample)*1000
            self.pixelsize.append(pixelsize)
        
        print('pixelsize bias +/- s.d.: {:.2f}'.format(np.mean(self.pixelsize))+' +/- {:.2f}'.format(np.std(self.pixelsize)))
    
    



if __name__ == "__main__":
    analyzer = AnalyzeHardcalibration(path=r'C:\Users\tvdrb\Desktop\Hardcalibration')
    analyzer.set_constants(stepsize=25, gamma=0.043767)
    analyzer.load_data_from_folder()
    analyzer.analyze_XY()
    analyzer.analyze_pixelsize()
