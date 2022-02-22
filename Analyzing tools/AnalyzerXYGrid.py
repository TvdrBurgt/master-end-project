# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:28:55 2022

@author: tvdrb
"""


import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patch




class XYGridGrounttruthProcessing:
    def __init__(self, path):
        self.folder = path
        self.groundtruth = np.ndarray([])
        self.step_size = 20
        self.offset = [0,0]
        
        self.image_size = [0,0]
        self.pixel_size = 0
        self.R = np.eye(3)
    
    
    def update_constants_from_JSON(self):
        with open(self.folder+'autopatch_configuration.txt', "r") as json_infile:
            data = json.load(json_infile)
        image_size = data["image_size"]
        pixelsize = data["pixel_size"]
        alpha,beta,gamma = data["rotation_angles"]
        self.set_image_size(image_size)
        self.set_pixel_size(pixelsize)
        self.set_rotation_matrix((-alpha,-beta,-gamma))
    
    
    def set_rotation_matrix(self, alphabetagamma):
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
        self.R = R_gamma @ R_beta @ R_alpha
    
    def set_image_size(self, dimesions):
        width,height = dimesions
        self.image_size = [width, height]
    
    def set_pixel_size(self, size):
        self.pixel_size = size
    
    @staticmethod
    def account4rotation(R, origin, target):
        return R[0:2,0:2] @ np.subtract(target,origin) + origin
    
    
    def load_raw_data(self):
        data = np.load(self.folder+'_imagexygrid_.npy')
        xs = data[0::2]
        ys = data[1::2]
        self.groundtruth = np.array([xs,ys])
    
    def rotate_data(self):
        origin = self.groundtruth[:,0]
        new_xs = np.array([])
        new_ys = np.array([])
        for i in range(0, self.groundtruth.shape[1]):
            target = self.groundtruth[:,i]
            new_x,new_y = self.account4rotation(self.R, origin, target)
            new_xs = np.append(new_xs, new_x)
            new_ys = np.append(new_ys, new_y)
        self.groundtruth = np.array([new_xs,new_ys])
    
    def convert_um_to_pix(self):
        Ox,Oy = self.groundtruth[:,0]
        self.groundtruth = self.groundtruth - np.array([[Ox],[Oy]])
        self.groundtruth = self.groundtruth / (self.pixel_size/1000)
        
    def compensate_origin_offset(self, dx, dy):
        self.offset = [dx,dy]
        self.groundtruth = self.groundtruth + np.array([[dx],[dy]])
    
    def plot_grid(self):
        plt.figure()
        plt.title('XY grid groundtruth')
        plt.xlabel('x (in pixels)'); plt.ylabel('y (in pixels)')
        plt.xlim([0, self.image_size[0]]); plt.ylim([self.image_size[1], 0])
        
        # make scatter plot
        groundtruth = self.groundtruth[:,1::2]
        colors = cm.rainbow(np.linspace(0, 1, groundtruth.shape[1]))
        xs,ys = groundtruth
        for i in range(groundtruth.shape[1]):
            plt.scatter(xs[i], ys[i], color=colors[i,:], marker='.')
        
        # add custom legend
        legend_elements = [plt.scatter([], [], marker='.', color='black', label='Ground truth')]
        plt.legend(handles=legend_elements)
        ax = plt.gca()
        ax.set_aspect('equal')
        # rectangle = patch.Rectangle((204, 204), 2048-204*2, 2048-204*2, linewidth=1, linestyle='--', edgecolor='black', facecolor='none')
        # ax.add_patch(rectangle)
        # plt.xticks([0, 204, 2048-204, 2048])
        # plt.yticks([0, 204, 2048-204, 2048])
        plt.xticks([0, self.image_size[0]])
        plt.yticks([0, self.image_size[1]])
        ax.xaxis.tick_top()





class XYGridAlgorithmProcessing:
    def __init__(self, path, filename):
        self.folder = path
        self.filename = filename
        self.algorithm = np.array([])
        self.name_coords = np.array([])
    
    def load_processed_data(self):
        algorithm = np.array([[],[]])
        coords = np.array([[],[]])
        with open(self.folder+self.filename, 'r') as csvfile:
            for line in csvfile:
                line = line.strip('\n')
                name,x,y = line.split(";")
                
                if name != 'filename':
                    # detected coordinates
                    coordinate = np.array([[float(x)],[float(y)]])
                    algorithm = np.append(algorithm, coordinate, axis=1)
                    
                    # file name for sorting later
                    name = name.strip('.tif')
                    X_idx = name.index('X')
                    Y_idx = name.index('Y')
                    xcoord = int(name[X_idx+1:Y_idx])
                    ycoord = int(name[Y_idx+1:-1])
                    coords = np.append(coords, np.array([[xcoord],[ycoord]]), axis=1)
        
        self.algorithm = algorithm
        self.name_coords = coords.astype(int)
    
    
    def sort_coordinates_from_name(self):
        name_coords_copy = self.name_coords
        algorithm_copy = self.algorithm
        
        # preprocessing
        xcoords,ycoords = name_coords_copy
        n_per_step = np.sum(xcoords==0)
        
        # sort on X coordinates
        xsorted_indices = xcoords.argsort()
        
        # sort Y coordinates per value of X
        ysorted_indices = np.zeros(n_per_step*n_per_step).astype(int)
        for i in range(0, n_per_step*n_per_step, n_per_step):
            ycoords_step = ycoords[xsorted_indices][i:i+n_per_step]
            ysorted_indices[i:i+n_per_step] = ycoords_step.argsort() + i
        
        # sorting the full array
        name_coords_copy = name_coords_copy[:,xsorted_indices]
        name_coords_copy = name_coords_copy[:,ysorted_indices]
        algorithm_copy = algorithm_copy[:,xsorted_indices]
        algorithm_copy = algorithm_copy[:,ysorted_indices]
        
        self.name_coords = name_coords_copy
        self.algorithm = algorithm_copy
    
    
    def plot_grid(self):
        plt.figure()
        plt.title('XY grid algorithm')
        plt.xlabel('x (in pixels)'); plt.ylabel('y (in pixels)')
        
        # make scatter plot
        colors = cm.rainbow(np.linspace(0, 1, self.algorithm.shape[1]))
        xs,ys = self.algorithm
        for i in range(self.algorithm.shape[1]):
            plt.scatter(xs[i], ys[i], color=colors[i,:], marker='x')
        
        # add custom legend
        legend_elements = [plt.scatter([], [], marker='x', color='black', label='Algorithm')]
        plt.legend(handles=legend_elements)
        ax = plt.gca()
        ax.set_aspect('equal')





class CompareEstimates:
    def __init__(self, groundtruth, algorithm):
        self.groundtruth = groundtruth
        self.algorithm = algorithm
        
        self.image_size = [0,0]
        self.boundary = [0,0]
    
    
    def set_image_size(self, size):
        self.image_size = size
        # self.boundary = [int(size[0]/10), int(size[1]/10)]
    
    
    def plot_grid(self):
        plt.figure()
        
        # set figure properties
        plt.title('Pipette tip localization comparison')
        plt.xlabel('x (in pixels)'); plt.ylabel('y (in pixels)')
        
        # make scatter plot
        x1,y1 = self.groundtruth[:,0::2]
        x2,y2 = self.algorithm
        colors = cm.rainbow(np.linspace(0, 1, self.algorithm.shape[1]))
        for i in range(self.algorithm.shape[1]):
            plt.scatter(x1[i], y1[i], color=colors[i,:], marker='x')
            plt.scatter(x2[i], y2[i], color=colors[i,:], marker='o')
        
        # add custom legend
        legend_elements = [plt.scatter([], [], marker='x', color='black', label='Ground truth'),
                           plt.scatter([], [], marker='o', color='black', label='Algorithm')]
        plt.legend(handles=legend_elements)
        
        # show plot
        plt.show()
    
    def plot_grid_in_boxes(self):
        n = 5
        
        groundtruth = self.groundtruth[:,0::2]
        algorithm = self.algorithm
        width = self.image_size[0]/n
        height = self.image_size[0]/n
        
        indices = []
        for i in range(0,n):
            for j in range(0,n):
                # define bounding box
                Xll = i*width
                Xul = i*width + width
                Yll = j*height
                Yul = j*height + height
                
                # store indices of datapoints belong to the current bounding box
                arr = np.where((groundtruth[0,:] < Xul) & (groundtruth[0,:] > Xll) & \
                               (groundtruth[1,:] < Yul) & (groundtruth[1,:] > Yll) & \
                               (groundtruth[0,:] < self.image_size[0])-self.boundary[0] & \
                               (groundtruth[0,:] > self.boundary[0]) & \
                               (groundtruth[1,:] < self.image_size[1])-self.boundary[1] & \
                               (groundtruth[1,:] > self.boundary[1]))
                indices.append(arr[0])
        
        # calculate bias and precision
        xbias = []
        ybias = []
        xprecision = []
        yprecision = []
        total_bias = []
        total_precision = []
        for idx_arr in indices:
            dx,dy = groundtruth[:,idx_arr] - algorithm[:,idx_arr]
            
            xmean = np.nanmean(dx)
            ymean = np.nanmean(dy)
            xsd = np.nanstd(dx)
            ysd = np.nanstd(dy)
            total_mean = np.nanmean(np.sqrt(dx**2 + dy**2))
            total_sd = np.nanstd(np.sqrt(dx**2 + dy**2))
            
            xbias.append(xmean)
            ybias.append(ymean)
            xprecision.append(xsd)
            yprecision.append(ysd)
            total_bias.append(total_mean)
            total_precision.append(total_sd)
        
        # print bias and standard deviation
        k = -1
        for i in range(0,n):
            for j in range(0,n):
                k +=1
                if i != 0 and i != n-1 and j != 0 and j != n-1:
                    print('grid ('+str(i)+','+str(j)+')')
                    print('Bias = {:.2f}'.format(total_bias[k])+' +/- {:.2f} s.d.'.format(total_precision[k]))
                # print('grid ('+str(i)+','+str(j)+')')
                # print('Bias = {:.2f}'.format(total_bias[k])+' +/- {:.2f} s.d.'.format(total_precision[k]))
        
        # visualize data
        plt.figure()
        plt.xlim([0, self.image_size[0]]); plt.ylim([self.image_size[1], 0])
        ax = plt.gca()
        colors = cm.rainbow(np.linspace(0, 1, n*n))
        k = -1
        for i in range(0,n):
            for j in range(0,n):
                k += 1
                center = (width*i+width/2, height*j+height/2)
                if xprecision[k] < 300 and yprecision[k] < 300:
                    ellipse = patch.Ellipse((center[0]+xbias[k], center[1]+ybias[k]), xprecision[k]*10, yprecision[k]*10, angle=0, ec=colors[k,:], fc='none', hatch='')
                    ax.add_patch(ellipse)
                    plt.scatter(center[0]+xbias[k], center[1]+ybias[k], color=colors[k,:], marker='+')
                plt.scatter(center[0], center[1], color=colors[k,:], marker='.')
        ax.set_aspect('equal')
        plt.xticks([0, self.boundary[0], self.image_size[0]-self.boundary[0], self.image_size[0]])
        plt.yticks([0, self.boundary[1], self.image_size[1]-self.boundary[1], self.image_size[1]])
        ax.xaxis.tick_top()
        # rectangle = patch.Rectangle((self.boundary[0], self.boundary[1]), self.image_size[0]-2*self.boundary[0], self.image_size[1]-2*self.boundary[1], linewidth=1, linestyle='--', edgecolor='black', facecolor='none')
        # ax.add_patch(rectangle)
        


if __name__ == "__main__":
    groundtruthanalyzer = XYGridGrounttruthProcessing(r'C:\Users\tvdrb\Desktop\2022-02-11 @ focus @ +30mBar/')
    groundtruthanalyzer.update_constants_from_JSON()
    groundtruthanalyzer.load_raw_data()
    groundtruthanalyzer.rotate_data()
    groundtruthanalyzer.convert_um_to_pix()
    groundtruthanalyzer.compensate_origin_offset(dx=32, dy=5)
    # groundtruthanalyzer.plot_grid()

    algorithmanalyzer = XYGridAlgorithmProcessing(r'C:\Users\tvdrb\Desktop\2022-02-11 @ focus @ +30mBar/','2022-02-11 @ focus @ +30mBar algorithm')
    algorithmanalyzer.load_processed_data()
    algorithmanalyzer.sort_coordinates_from_name()
    algorithmanalyzer.plot_grid()
    
    visualizer = CompareEstimates(groundtruthanalyzer.groundtruth, algorithmanalyzer.algorithm)
    visualizer.set_image_size(groundtruthanalyzer.image_size)
    # visualizer.plot_grid()
    visualizer.plot_grid_in_boxes()
