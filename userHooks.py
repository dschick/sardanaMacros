# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: korff
"""
from sardana.macroserver.macro import macro
import time
from dirsync import sync
import os

@macro()
def userPreAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    waittime = acqConf['waitTime']
    
    if waittime:
        time.sleep(waittime)
        self.info('waiting for %.2f s', waittime)
        
    if altOn:
        #self.info("pre-acq hook altOn")
        # move magnet to minus amplitude
        magnConf = self.getEnv('magnConf')
        ampl = magnConf['ampl']
        magwaittime = magnConf['waitTime']
        kepco = self.getMotor("kepco")
        kepco.move(-1*ampl)
        time.sleep(magwaittime)
        
        parent = self.getParentMacro()
        if parent:
            integ_time = parent.integ_time
#            mg = parent._gScan.measurement_group
#            mg.count(integ_time)    
            self.execMacro('ct_altOn', integ_time)
                       
        kepco.move(+1*ampl)
        time.sleep(magwaittime)
        
    else:
        #self.info("pre-acq hook altOff")
        pass
    
@macro()
def userPostAcq(self):
    acqConf = self.getEnv('acqConf')
    altOn = acqConf['altOn']
    
    if altOn:
        #self.info("post-acq hook altOn")
        # move magnet to minus amplitude
        pass
           
    else:
        #self.info("post-acq hook altOff")
        pass
    
@macro()
def userPostScan(self):
    ScanDir = self.getEnv('ScanDir')
    RemoteScanDir = self.getEnv('RemoteScanDir')
        
    if os.path.exists(RemoteScanDir):
        self.info('Syncing data from %s to %s', ScanDir, RemoteScanDir)
        sync(ScanDir, RemoteScanDir, 'sync', create=True)        
    else:
        self.warning('RemoteScanDir %s does not exist - no folder syncing', RemoteScanDir)
    
    