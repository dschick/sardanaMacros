# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: korff
"""
from sardana.macroserver.macro import macro, Type
import time
from datetime import datetime
from dirsync import sync
import os
from PyTango import DeviceProxy

@macro()
def userPreAcq(self):
    acqConf  = self.getEnv('acqConf')
    altOn    = acqConf['altOn']
    waittime = acqConf['waitTime']
    parent = self.getParentMacro()
    
    scanDir  = self.getEnv('ScanDir')
    scanFile = self.getEnv('ScanFile')[0].replace('.', '_')
    scanID = self.getEnv('ScanID')
    geCtrl = DeviceProxy('controller/greateyescountertimercontroller/greateyesctrl')
    
    now = datetime.today().strftime("%Y%m%d_%H%M%S_%f")
#    now = now.strftime()
    
    # check if this is a ct
    if parent and (parent._name == 'ct'):
        fileName = '{:s}{:s}/ct/{:s}'.format(scanDir, scanFile, now)
        fileName = fileName[1:]
        geCtrl.pointnb = -1
    elif parent: # it is a scan
        fileName = '{:s}{:s}/{:d}/'.format(scanDir, scanFile, scanID)
        fileName = fileName[1:]
        pointNb = geCtrl.pointnb
        geCtrl.pointnb = pointNb + 1
    else:
        fileName   = ''
        
        
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
        
        
        if parent:
            self.debug('do pre-acquisition ...')            
            fileNameMinus = fileName + 'M'
            self.debug(fileNameMinus)
            geCtrl.filename = fileNameMinus
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
    
    
    self.debug(fileName)
    geCtrl.filename = fileName
    
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
        # reset pointNb to 0
        geCtrl = DeviceProxy('controller/greateyescountertimercontroller/greateyesctrl')
        geCtrl.pointnb = 0
    
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
    
    