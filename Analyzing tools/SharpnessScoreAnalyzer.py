# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 21:15:37 2022

@author: tvdrb
"""


import numpy as np
import matplotlib.pyplot as plt
from skimage import io, filters


class AnalyzeSharpnessScores:
    def __init__(self, path):
        self.image_stack_path = path
        self.zstack = None
        self.zpos = []
        self.sharpness_variance = []
        self.sharpness_sobel = []
        self.sharpness_laplacian = []
    
    
    def loadZstack(self):
        self.zstack = io.imread(self.image_stack_path)
    
    
    def loadZpos(self, positions):
        self.zpos = positions
    
    
    def varianceOfImage(self, img):
        # average images
        img_average = filters.gaussian(img, 4)
        
        # calculate variance
        penalty = np.var(img_average)
        
        return penalty
    
    
    def varianceOfSobel(self, img):
        # average images
        img_average = filters.gaussian(img, 4)
        
        # calculate sobel
        img_sobel = np.sqrt(filters.sobel_h(img_average)**2 + filters.sobel_v(img_average)**2)
        
        # average variance
        penalty = np.var(img_sobel)
        
        return penalty
    
    
    def varianceOfLaplacian(self, img):
        # average images
        img_average = filters.gaussian(img, 4)
        
        # calculate laplacian
        img_laplace = filters.laplace(img_average, 3)
        
        # calculate variance
        penalty = np.var(img_laplace)
        
        return penalty

    
    def iterator(self):
        """
        This function iterates over all images in the Z stack and calculates the
        out-of-focus penalty per image.
        """
        # get Z-stack dimensions
        depth, height, width = self.zstack.shape
        
        print("Calculating penalties...")
        self.sharpness_variance = np.empty(depth)
        self.sharpness_sobel = np.empty(depth)
        self.sharpness_laplacian = np.empty(depth)
        for i in range(depth):
            img = self.zstack[i]
            self.sharpness_variance[i] = self.varianceOfImage(img)
            self.sharpness_sobel[i] = self.varianceOfSobel(img)
            self.sharpness_laplacian[i] = self.varianceOfLaplacian(img)
            print(i)
            print(str(self.sharpness_variance[i]) + ' ' + str(self.sharpness_sobel[i]) + ' ' + str(self.sharpness_laplacian[i]))
        print('finished')
    
    def visualize(self):
        int_variance = np.sum(self.sharpness_variance)
        int_sobel = np.sum(self.sharpness_sobel)
        int_laplacian = np.sum(self.sharpness_laplacian)
        
        plt.figure()
        plt.plot(self.zpos, self.sharpness_variance/int_variance, linestyle='--', label='Variance')
        plt.plot(self.zpos, self.sharpness_sobel/int_sobel, linestyle='-.', label='Sobel')
        plt.plot(self.zpos, self.sharpness_laplacian/int_laplacian, linestyle=':', label='Laplacian')
        plt.xlabel('Height (in µm)'); plt.ylabel('Sharpness score')
        plt.legend()
    
    def removePoint(self, k):
        self.sharpness_variance = np.delete(self.sharpness_variance, k)
        self.sharpness_sobel = np.delete(self.sharpness_sobel, k)
        self.sharpness_laplacian = np.delete(self.sharpness_laplacian, k)
        self.zpos = np.delete(self.zpos, k)
        
    

if __name__ == "__main__":
    # Translate in Z, #24 corresponds to z=0
    zpos_2021_03_03 = np.concatenate([np.arange(-350, -250, 50),
                                      np.arange(-250, -100, 25),
                                      np.arange(-100, -50, 10),
                                      np.arange(-50, -10.001, 5),
                                      np.arange(0, 5.001, 1),
                                      np.arange(5, 100, 10),
                                      np.arange(100, 500, 50),
                                      np.arange(500, 1000, 100),
                                      np.arange(1000, 2000, 250),
                                      np.arange(2000, 3000.001, 500)])
    # Z stack 2021-03-18, #85 corresponds to z=0
    zpos_2021_03_18 = np.concatenate([np.arange(-300, -250, 50),
                                      np.arange(-250, -100, 25),
                                      np.arange(-100, -50, 10),
                                      np.arange(-50, -3, 1),
                                      np.arange(-3, -2.5, 0.5),
                                      np.arange(-2.5, 5, 0.1),
                                      np.arange(5, 50, 1),
                                      np.arange(50, 100, 10),
                                      np.arange(100, 250, 25),
                                      np.arange(250, 500, 50),
                                      np.arange(500, 2000.001, 100)])
    # Z stack 2021-03-23, #13 corresponds to z=0
    zpos_2021_03_23 = np.concatenate([np.arange(-30, -10, 10),
                                      np.arange(-10, 0.001, 1),
                                      np.arange(0, 10, 1),
                                      np.arange(10, 100, 10),
                                      np.arange(100, 200.001, 100)])
    
    # analyzer = AnalyzeSharpnessScores(path=r"C:\Users\tvdrb\Desktop\Z stack 2021-03-03.tif")
    analyzer = AnalyzeSharpnessScores(path=r"C:\Users\tvdrb\Desktop\Z stack 2021-03-18.tif")
    # analyzer = AnalyzeSharpnessScores(path=r"C:\Users\tvdrb\Desktop\Z stack 2021-03-23.tif")
    analyzer.loadZstack()
    # analyzer.loadZpos(zpos_2021_03_03)
    analyzer.loadZpos(zpos_2021_03_18)
    # analyzer.loadZpos(zpos_2021_03_23)
    analyzer.iterator()
    analyzer.removePoint(181)
    analyzer.visualize()
    


def visualize(AnalyzeSharpnessScores):
    int_variance = np.sum(analyzer.sharpness_variance)
    int_sobel = np.sum(analyzer.sharpness_sobel)
    int_laplacian = np.sum(analyzer.sharpness_laplacian)
    
    plt.figure()
    # plt.plot(analyzer.zpos, analyzer.sharpness_variance/int_variance, linestyle='--', label='Variance')
    plt.plot(analyzer.zpos, analyzer.sharpness_sobel/int_sobel, linestyle='-.', label='Sobel')
    plt.plot(analyzer.zpos, analyzer.sharpness_laplacian/int_laplacian, linestyle=':', label='Laplacian')
    plt.xlabel('Height (in µm)'); plt.ylabel('Sharpness score')
    plt.legend()