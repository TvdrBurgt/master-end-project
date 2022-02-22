# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 21:52:43 2022

@author: tvdrb
"""


import numpy as np


  
class AnalyzeAutopatch:
    def __init__(self, path):
        self.folder = path
        self.T_precheck = []
        self.T_autofocus = []
        self.T_softcalibration = []
        self.T_correction = []
        self.T_approach = []
        self.T_seal = []
        self.T_breakin = []
        self.T_reset = []
        self.T_success = []
    
    
    def analyze_raw_data(self, folder_name):
        with open(self.folder+'\\'+folder_name+'\\time deltas.txt', 'r') as csvfile:
            for line in csvfile:
                date,pre,aut,sof,cor,app,sea,bre,res,suc = line.split(';')
                if date != 'date':
                    if aut !='null':
                        self.T_autofocus.append(float(aut))
                    if sof !='null':
                        self.T_softcalibration.append(float(sof))
                    if app !='null':
                        self.T_approach.append(float(app))
                    if sea !='null':
                        self.T_seal.append(float(sea))
                    if bre !='null':
                        self.T_breakin.append(float(bre))
                    if res !='null':
                        self.T_reset.append(float(res))
    
    def print_results(self):
        print('Autofocus time: {:.2f} min'.format(np.mean(self.T_autofocus)))
        print('Calibration time: {:.2f} min'.format(np.mean(self.T_softcalibration)))
        print('Approach+correction time: {:.2f} min'.format(np.mean(self.T_approach)))
        print('Gigaseal time: {:.2f} min'.format(np.mean(self.T_seal)))
        print('Breakin time: {:.2f} min'.format(np.mean(self.T_breakin)))
        print('Reset+checks time: {:.2f} min'.format(np.mean(self.T_reset)))





if __name__ == "__main__":
    analyzer = AnalyzeAutopatch(path=r'C:\Users\tvdrb\Desktop\Autopatch')
    analyzer.analyze_raw_data('2022-2-11')
    analyzer.print_results()
