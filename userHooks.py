# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: korff
"""
from sardana.macroserver.macro import macro

@macro()
def userPreAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    
    if altOn:
        self.output("pre-acq hook altOn")
    else:
        self.output("pre-acq hook altOff")
    


@macro()
def userPostAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    
    if altOn:
        self.output("pre-acq hook altOn")
    else:
        self.output("pre-acq hook altOff")
    