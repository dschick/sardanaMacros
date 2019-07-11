# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: korff
"""
from sardana.macroserver.macro import macro, Type
import time
from dirsync import sync
import os
from PyTango import DeviceProxy

@macro()
def userPreAcq(self):
    acqConf  = self.getEnv('acqConf')
    altOn    = acqConf['altOn']
    waittime = acqConf['waitTime']
    
    if waittime:
        self.debug('waittime is set ...')
        time.sleep(waittime)
        self.debug('waiting for %.2f s', waittime)
        
    if altOn:
        self.debug('alton is set ...')
        # move magnet to minus amplitude
        self.debug('reading the environment ...')
        magnConf    = self.getEnv('magnConf')
        ampl        = magnConf['ampl']
        magwaittime = magnConf['waitTime']
        self.debug('accessing the magnet ...')
        magnet      = self.getMotion(["kepco"])
        self.debug('accessing the magnet state ...')
        magnetState = DeviceProxy("hhg/MagnetState/xmcd")
        
        self.debug('move the magnet -1 ...')
        magnet.move(-1*ampl)        
        self.debug('change the magnet state -1 ...')
        magnetState.magnet = -1*ampl
        
        self.debug('mag. waiting for %.2f s', magwaittime)
        time.sleep(magwaittime)        
        
        parent = self.getParentMacro()
        if parent:
            self.debug('do pre-acquisition ...')
            integ_time  = parent.integ_time
            mnt_grp     = self.getObj(self.getEnv('ActiveMntGrp'), type_class=Type.MeasurementGroup)
            state, data = mnt_grp.count(integ_time)

        self.debug('move the magnet +1 ...')
        magnet.move(+1*ampl)
        self.debug('change the magnet state +1 ...')
        magnetState.magnet = +1*ampl
        
        self.debug('mag. waiting for %.2f s', magwaittime)
        time.sleep(magwaittime)                
    else:
        self.debug('alton is off ...')
    
@macro()
def userPreScan(self):
    # print the current configuration with macros like:
    # acqrep, magnrep, fluencerep, powerrep
    
    parent = self.getParentMacro()
    if parent: # macro is called from another macro
        self.execMacro('send2ctrl greateyesCtrl set_exposure 0 {:}'.format(parent.integ_time))
        self.execMacro('send2ctrl greateyesCtrl set_exposure 1 {:}'.format(parent.integ_time)) 
        self.execMacro('send2ctrl greateyesCtrl dark 0')
        self.execMacro('send2ctrl greateyesCtrl dark 1')
    
    self.execMacro('acqrep')
        
@macro()
def userPostScan(self):
    ScanDir = self.getEnv('ScanDir')
    RemoteScanDir = self.getEnv('RemoteScanDir')
        
    if os.path.exists(RemoteScanDir):
        self.info('Syncing data from %s to %s', ScanDir, RemoteScanDir)
        sync(ScanDir, RemoteScanDir, 'sync', create=True)        
    else:
        self.warning('RemoteScanDir %s does not exist - no folder syncing', RemoteScanDir)
    
    