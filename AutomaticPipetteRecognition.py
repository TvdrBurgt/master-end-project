# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:17:08 2021

@author: tvdrb
"""

import os
import numpy as np
from skimage import io, filters, feature, transform, draw
import matplotlib.pyplot as plt


# =============================================================================
# Automatic Pipette Recognition
# =============================================================================


class DetectPipetteTips:
    """"
    This class iterates through a folder containing .tif files and extracts the
    (x,y)-coordinates of pipette tips.
    """
    def __init__(self,path):
        self.folder = path
        self.savename = "Translation space Boyden"
        self.filenames = os.listdir(path)
        self.filecount = -1
        self.lastfile = len(self.filenames)
        self.pipettetips = []                   # estimated tip coordinates
        
        
    def nextImage(self):
        """
        This function calls the pipette recognition algorithm for the next .tif
        file. It also checks if it has reached the last file in the folder.
        """
        self.filecount += 1
        print("File number %d/%d" % (self.filecount+1,self.lastfile))
        
        # check if we arrived at the last file
        if self.filecount < self.lastfile:
            filepath = self.folder + "\\" + str(self.filenames[self.filecount])
            
            # check if file is a .tif before opening
            if filepath.endswith('.tif'):
                self.I = io.imread(filepath)
                # run pipette tip recognition algorithm
                self.pipetteRecognition()
            self.nextImage()
                
        else:
            print("Last file in folder reached")
            self.list2file()
    
    def pipetteRecognition(self):
        """
        This function contains the pipette recognition algorithm itself. It
        performs the image analysis steps and finds a maximum number of lines
        [num_lines] to describe the pipette point. The intersection should be
        the pipette tip.
        """
        num_lines = 7 # maximum number of lines to find
        
        print('I) Gaussian blurring...')
        IB = filters.gaussian(self.I, 15)
        
        print('II) Canny edge detection...')
        BW = feature.canny(IB, sigma=10, low_threshold=0.9, high_threshold=0.7, use_quantiles=True)
        
        print('III) Calculating Hough transform...')
        self.H, self.T, self.R = transform.hough_line(BW,np.linspace(5*np.pi/12,7*np.pi/12,120*100))
        
        print('IV) Finding most common lines from Hough transform...')
        _, self.Tcommon, self.Rcommon = transform.hough_line_peaks(self.H,self.T,self.R,num_peaks=num_lines)
        
        print('V) Filling canvas with most the %d most common lines...' % num_lines)
        self.canvas = np.zeros((self.I.shape[0], self.I.shape[1]))
        for r0, c0, r1, c1 in zip(*self.Houghlines2Imageboundary(self.Tcommon,self.Rcommon,self.I)):
            rr, cc = draw.line(r0, c0, r1, c1)
            self.canvas[rr, cc] += 1
        self.canvas = filters.gaussian(self.canvas, 5)
        
        # extract pipette tip
        ypos, xpos = np.where(self.canvas == np.max(self.canvas))
        if len(xpos) != 1:
            ypos = ypos[0]
            xpos = xpos[0]
        print('VI) Pipette tip located at pixel coordinate: (x,y) = (%d,%d).' % (xpos,ypos))
        
        # saving pipette tip coordinates
        self.pipettetips.append([self.filenames[self.filecount], (xpos, ypos)])
        
        # plot result
        # self.plotFigures()
        
        # go to next file
        self.nextImage()
        
        
    def Houghlines2Imageboundary(self,T,R,img):
        """
        This function extracts the intersection coordinates between extended Hough-
        lines with the image boundary. The output are the rows and columns of the
        image where the infinite Houghlines leave/enter the image.
        """
        # get width and height of image
        height = img.shape[0]
        width = img.shape[1]
        
        # divide angles into parallel and perpundicular to prevent exploding slopes
        cutoff = np.abs(np.sin(T))
        Tpar = T[np.where(cutoff >= np.sqrt(2)/2)]
        Rpar = R[np.where(cutoff >= np.sqrt(2)/2)]
        Tperp = T[np.where(cutoff < np.sqrt(2)/2)]
        Rperp = R[np.where(cutoff < np.sqrt(2)/2)]
        
        # determine a and b in y=ax+b (parallel)
        a = np.tan(np.pi/2+Tpar)
        b = Rpar/np.sin(Tpar)
        # determine c and d in x=cy+d (perpundicular)
        c = np.tan(-Tperp)
        d = Rperp/np.cos(Tperp)
        
        # prevent dividing by zero in the next step
        a[a==0] = 1e-9
        c[c==0] = 1e-9
        
        # determine crossings with the lines: y=0, x=0, y=height, x=width (parallel)
        x0 = -b/a
        y0 = b
        xh = (height-b)/a
        yw = a*width + b
        # determine crossings with the lines: y=0, x=0, y=height, x=width (perpundicular)
        x_0 = d
        y_0 = -d/c
        x_h = c*height + d
        y_w = (width-d)/c
        
        # place crossings on the image edge (parallel)
        x0[x0>width-1] = width-1
        x0[x0<0] = 0
        y0[y0>height-1] = height-1
        y0[y0<0] = 0
        xh[xh>width-1] = width-1
        xh[xh<0] = 0
        yw[yw>height-1] = height-1
        yw[yw<0] = 0
        # place crossings on the image edge (perpundicular)
        x_0[x_0>width-1] = width-1
        x_0[x_0<0] = 0
        y_0[y_0>height-1] = height-1
        y_0[y_0<0] = 0
        x_h[x_h>width-1] = width-1
        x_h[x_h<0] = 0
        y_w[y_w>height-1] = height-1
        y_w[y_w<0] = 0
        
        # match coordinates (parallel)
        xleft = np.zeros((len(Tpar)))
        yleft = np.zeros((len(Tpar)))
        xright = np.zeros((len(Tpar)))
        yright = np.zeros((len(Tpar)))
        for i in range(len(Tpar)):
            xleft[i] = np.min([x0[i],xh[i]])
            xright[i] = np.max([x0[i],xh[i]])
            if a[i] > 0:
                yleft[i] = np.min([y0[i],yw[i]])
                yright[i] = np.max([y0[i],yw[i]])
            else:
                yleft[i] = np.max([y0[i],yw[i]])
                yright[i] = np.min([y0[i],yw[i]])
        # match coordinates (perpundicular)
        x_left = np.zeros((len(Tperp)))
        y_left = np.zeros((len(Tperp)))
        x_right = np.zeros((len(Tperp)))
        y_right = np.zeros((len(Tperp)))
        for i in range(len(Tperp)):
            x_left[i] = np.min([x_0[i],x_h[i]])
            x_right[i] = np.max([x_0[i],x_h[i]])
            if c[i] > 0:
                y_left[i] = np.min([y_0[i],y_w[i]])
                y_right[i] = np.max([y_0[i],y_w[i]])
            else:
                y_left[i] = np.max([y_0[i],y_w[i]])
                y_right[i] = np.min([y_0[i],y_w[i]])
                
        # let x and y be rows and columns (parallel)
        c0 = np.around(xleft).astype(int)
        r0 = np.around(yleft).astype(int)
        c1 = np.around(xright).astype(int)
        r1 = np.around(yright).astype(int)
        # let x and y be rows and columns (perpundicular)
        c_0 = np.around(x_left).astype(int)
        r_0 = np.around(y_left).astype(int)
        c_1 = np.around(x_right).astype(int)
        r_1 = np.around(y_right).astype(int)
        
        # append coordinates from parallel and perpundicular lines
        C0 = np.append(c0,c_0)
        R0 = np.append(r0,r_0)
        CW = np.append(c1,c_1)
        RH = np.append(r1,r_1)
        
        return R0, C0, RH, CW
    
    
    def plotFigures(self):
        xpos = self.pipettetips[-1][1]
        ypos = self.pipettetips[-1][2]
        
        f1, axs1 = plt.subplots(1,3)
        axs1[0].imshow(self.I, cmap='gray'); axs1[0].axis('image'); axs1[0].axis('off')
        axs1[0].scatter(x=xpos, y=ypos, c='r', s=30)
        axs1[0].annotate('(%d,%d)' % (xpos,ypos), (xpos+30, ypos-15), c='r')
        axs1[1].imshow(self.canvas, cmap='gray'); axs1[1].axis('image'); axs1[1].axis('off')
        axs1[2].imshow(np.log(1+self.H), extent=[np.rad2deg(self.T[0]), np.rad2deg(self.T[-1]), self.R[-1], self.R[0]], aspect='auto')
        axs1[2].set_xlabel(r'$\theta$ (degree)')
        axs1[2].set_ylabel(r'$\rho$ (pixels)')
        
        for i in range(0, len(self.Rcommon)):
            axs1[2].scatter(x=[self.Tcommon[i]*180/np.pi], y=[self.Rcommon[i]], c='r', s=20)
        
        plt.pause(10)
        input("Press enter to continue...")
        plt.close()
        
    
    def list2file(self):
        # write final coordinates to a .csv file
        with open(self.folder+'\\'+self.savename, 'w') as txtfile:
            txtfile.write("filename;x;y\n")
            # for item in self.pipettetips:
            #     txtfile.write("{};".format(item[0]))
            #     try:
            #         txtfile.write("%d;" % item[1][0])
            #     except:
            #         txtfile.write("%d;" % item[1])
            #     try:
            #         txtfile.write("%d\n" % item[2][0])
            #     except:
            #         txtfile.write("%d\n" % item[2])
            for item in self.pipettetips:
                txtfile.write("{};".format(item[0]))
                txtfile.write("%d;" % item[1][0])
                txtfile.write("%d\n" % item[1][1])
        print("Files saved in [path] with name {}".format(self.savename))


if __name__ == '__main__':
    # fill in the complete path of the folder containing pipette tip images
    path = r"C:\Users\tvdrb\Desktop\Thijs\Translation space"
    
    pipettetips = DetectPipetteTips(path)
    pipettetips.nextImage()
    
    