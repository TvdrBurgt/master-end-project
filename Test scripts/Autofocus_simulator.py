# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 17:16:18 2021

@author: tvdrb
"""


import numpy as np
import matplotlib.pyplot as plt

class autofocus:
    def __init__(self, start, fz, z):
        # groundtruth
        self.fz = fz
        self.z = z
        
        # autofocus
        self.stepsize = 10
        self.focusbias = 20
        self.n = 12
        self.reference = start
        self.penaltyhistory = np.array([])
        self.positionhistory = np.array([])
        self.lookingforpeak = False
    
    def getSharpnessgraph(self):
        return np.vstack([self.positionhistory, self.penaltyhistory])
    
    def start(self):
        #I) fill first three sharpness scores towards the tail of the graph
        self.pen = np.zeros(3)
        self.pos = np.zeros(3)
        for i in range(0,3):
            self.pos[i] = self.reference + (i+1)*self.stepsize
            self.pen[i] = self.fz[np.where(self.z == self.pos[i])]
        self.penaltyhistory = np.append(self.penaltyhistory, self.pen)
        self.positionhistory = np.append(self.positionhistory, self.pos)
        
        self.going_up = True
        self.going_down = not self.going_up
        self.lookingforpeak = True
    
    def epoch(self):
        #II) check which side of the sharpness graph to extend
        move = None
        if self.going_up:
            self.pen = self.penaltyhistory[-3::]
        else:
            self.pen = self.penaltyhistory[0:3]
        
        #III) check where maximum penalty score is: left, middle, right
        if np.argmax(self.pen) == 0:
            maximum = 'left'
        elif np.argmax(self.pen) == 1:
            maximum = 'middle'
        elif np.argmax(self.pen) == 2:
            maximum = 'right'
        
        #IVa) possible actions to undertake while going up
        if maximum == 'right' and self.going_up:
            move = 'step up'
        elif maximum == 'left' and self.going_up:
            self.going_up = False
            self.going_down = True
        elif maximum == 'middle' and self.going_up:
            if self.pen[1] == np.max(self.penaltyhistory):
                self.pos = self.positionhistory[-1]
                self.penaltytail = self.pen[1::]
                k = 0
                for i in range(2, self.n):
                    k = k+1
                    penalty = self.fz[np.where(self.z == self.pos+self.stepsize*k)]
                    penaltytail = np.append(self.penaltytail, penalty)
                differences = np.diff(penaltytail)
                monotonicity_condition = np.all(differences <= 0)
                if monotonicity_condition:
                    print("Detected maximum is a sharpness peak! (1)")
                    self.lookingforpeak = False
                else:
                    print("Detected maximum is noise")
                    self.going_up = False
                    self.going_down = True
            else:
                self.going_up = False
                self.going_down = True
        
        #IVb) possible actions to undertake while going down
        elif maximum == 'left' and self.going_down:
            move = 'step down'
        elif maximum == 'right' and self.going_down:
            if self.pen[2] == np.max(self.penaltyhistory):
                self.pos = self.positionhistory[2]
                penaltytail = self.pen[2]
                k = 0
                for i in range(2, self.n):
                    k = k+1
                    penalty = self.fz[np.where(self.z == self.pos+self.stepsize*k)]
                    penaltytail = np.append(penaltytail, penalty)
                monotonicity_condition = np.all(np.diff(penaltytail) <= 0)
                if monotonicity_condition:
                    print("Detected maximum is a sharpness peak! (2)")
                    self.lookingforpeak = False
                else:
                    print("Detected maximum is noise")
                    move = 'step down'
            else:
                move = 'step down'
        elif maximum == 'middle' and self.going_down:
            penaltytail = self.penaltyhistory[1::]
            taillength = len(penaltytail)
            if taillength < self.n:
                self.pos = self.positionhistory[-1]
                k = 0
                for i in range(taillength, self.n):
                    k = k+1
                    penalty = self.fz[np.where(self.z == self.pos+self.stepsize*k)]
                    penaltytail = np.append(penaltytail, penalty)
            else:
                penaltytail = penaltytail[0:self.n]
            monotonicity_condition = np.all(np.diff(penaltytail) <= 0)
            if monotonicity_condition:
                print("Detected maximum is a sharpness peak! (3)")
                self.lookingforpeak = False
            else:
                print("Detected maximum is noise")
                move = 'step down'
    
        #V) extend the sharpness function on either side
        if move == 'step up':
            self.pos = self.positionhistory[-1] + self.stepsize
            pen = self.fz[np.where(self.z == self.pos)]
            self.penaltyhistory = np.append(self.penaltyhistory, pen)
            self.positionhistory = np.append(self.positionhistory, self.pos)
        elif move == 'step down':
            self.pos = self.positionhistory[0] - self.stepsize
            pen = self.fz[np.where(self.z == self.pos)]
            self.penaltyhistory = np.append(pen, self.penaltyhistory)
            self.positionhistory = np.append(self.pos, self.positionhistory)


if __name__ == "__main__":
    np.random.seed(34576)
    
    z = np.linspace(-50,2000,2051)
    fz = (1/np.sqrt(2*np.pi*300**2))*np.exp(-z**2/2/300**2) + (1/np.sqrt(2*np.pi*100**2))*np.exp(-z**2/2/100**2) + z/100**4
    fz_noise = fz + (np.random.rand(len(z))-0.5)/10*(2/2051)
    
    n_agents = 10
    agents_position_history = np.zeros((n_agents,3))
    agents_penalty_history = np.zeros((n_agents,3))
    for i in range(0,n_agents):
        agent = autofocus(1800+(np.random.randint(50)-25), fz_noise, z)
        agent.start()
        while agent.lookingforpeak:
            agent.epoch()
        agents_position_history[i,:] = agent.positionhistory[0:3]
        agents_penalty_history[i,:] = agent.penaltyhistory[0:3]
    
    plt.figure()
    # plt.plot(z, fz, label="$s(z)$", color = 'blue')
    plt.scatter(z, fz_noise, label="$S_{sim}(z)$", marker='2', color='grey')
    positionhistory, penaltyhistory = agent.getSharpnessgraph()
    plt.plot(positionhistory, penaltyhistory, label="agent", color='yellow')
    plt.title("Simulation of sharpness function")
    plt.xlabel(r'Focus depth (in $\mu$m)')
    plt.ylabel(r'Variance of Laplacian (a.u.)')
    plt.legend()
    
    plt.figure()
    for i in range(0,n_agents):
        plt.plot(agents_position_history[i,:], agents_penalty_history[i,:], label='agent '+str(i+1))
    plt.title("3-point end of pipettetip autofocus (n=12)")
    plt.xlabel(r'Focus depth (in $\mu$m)')
    plt.ylabel(r'Variance of Laplacian (a.u.)')
    plt.legend()
    