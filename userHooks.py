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
from PyTango import AttributeProxy

@macro()
def userPreAcq(self):
    try:
        acqConf  = self.getEnv('acqConf')
        altOn    = acqConf['altOn']
        waittime = acqConf['waitTime']
        parent = self.getParentMacro()
        
        scanDir  = self.getEnv('ScanDir')
        scanFile = self.getEnv('ScanFile')[0].replace('.', '_')
        scanID = self.getEnv('ScanID')
    except:
        self.error('Error while reading environment in userPreAcq')
        
    try:
        geCtrlFileName = AttributeProxy('controller/greateyescountertimercontroller/greateyesctrl/filename')
        geCtrlPointNB = AttributeProxy('controller/greateyescountertimercontroller/greateyesctrl/pointnb')
    except:
         self.error('Error while creating AttributeProxy of greateyes')
    
    now = datetime.today().strftime("%Y%m%d_%H%M%S_%f")
#    now = now.strftime()
    
    # check if this is a ct
    if parent and (parent._name == 'ct'):
        fileName = '{:s}{:s}/ct/{:s}'.format(scanDir, scanFile, now)
        fileName = fileName[1:]
        try:
            geCtrlPointNB.write(-1)
        except:
            self.error('Error while writing point Nb to greateyes')
    elif parent: # it is a scan
        fileName = '{:s}{:s}/{:d}/'.format(scanDir, scanFile, scanID)
        fileName = fileName[1:]
        try:
            pointNb = geCtrlPointNB.read().value
            geCtrlPointNB.write(pointNb + 1)
        except:
            self.error('Error while read/writing point Nb to greateyes')
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
        magnet      = self.getMotion(["magnet"])
        self.debug('accessing the magnet state ...')
        magnetState = AttributeProxy("hhg/MagnetState/xmcd/magnet")
        
        self.debug('move the magnet -1 ...')
        magnet.move(-1*ampl)        
        self.debug('change the magnet state -1 ...')
        magnetState.write(-1*ampl)
        
        self.debug('mag. waiting for %.2f s', magwaittime)
        time.sleep(magwaittime)        
        
        
        if parent:
            self.debug('do pre-acquisition ...')            
            fileNameMinus = fileName + 'M'
            self.debug(fileNameMinus)
            try:
                geCtrlFileName.write(fileNameMinus)
            except:
                self.error('Error while writing filename to greateyes')
            integ_time  = parent.integ_time
            mnt_grp     = self.getObj(self.getEnv('ActiveMntGrp'), type_class=Type.MeasurementGroup)
            state, data = mnt_grp.count(integ_time)

        self.debug('move the magnet +1 ...')
        magnet.move(+1*ampl)
        self.debug('change the magnet state +1 ...')
        magnetState.write(+1*ampl)
        
        self.debug('mag. waiting for %.2f s', magwaittime)
        time.sleep(magwaittime)                
    else:
        self.debug('alton is off ...')    
    
    self.debug(fileName)
    try:
        geCtrlFileName.write(fileName)
    except:
        self.error('Error while writing filename to greateyes')
    self.debug('End of userPreAcq')
    
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
        time.sleep(1.2*parent.integ_time)
        # reset pointNb to 0
        geCtrlPointNB = AttributeProxy('controller/greateyescountertimercontroller/greateyesctrl/pointnb')
        geCtrlPointNB.write(0)
    
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


    
    
