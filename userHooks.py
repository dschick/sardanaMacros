# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: korff
"""
from sardana.macroserver.macro import macro
import time

@macro()
def userPreAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    waittime = acqConf['waittime']
    
    if waittime:
        time.sleep(waittime)
        self.info('waiting for %f', waittime)
    
    
    if altOn:
        self.info("pre-acq hook altOn")
        # move magnet to minus amplitude
        magnConf = self.getEnv('magnConf')
        ampl = magnConf['ampl']
        kepco = self.getMotor("kepco")
        kepco.move(-1*ampl)
    else:
        self.info("pre-acq hook altOff")
    


@macro()
def userPostAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    
    if altOn:
        self.info("post-acq hook altOn")
        # move magnet to minus amplitude
        magnConf = self.getEnv('magnConf')
        ampl = magnConf['ampl']
        kepco = self.getMotor("kepco")
        kepco.move(+1*ampl)
        
        parent = self.getParentMacro()
        if parent:
            integ_time = parent.integ_time
            mg = parent._gScan.measurement_group
            mg.count(integ_time)        
    else:
        self.info("post-acq hook altOff")
    