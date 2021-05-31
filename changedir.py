# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:57:08 2018

@author: embeh
"""
from sardana.macroserver.macro import imacro, macro, Macro, Type, Optional, ParamRepeat
import time
from dirsync import sync
import os
from PyTango import DeviceProxy

@macro() #muss vor jedem Macro stehen
def change_remote_dir(self): #change synch dir, this is the command in spock
    self.setEnv('RemoteScanDir','/media/nas/data/trXMCD/MBI/Sardana/201912')
    RemoteScanDir = self.getEnv('RemoteScanDir')
    self.output(RemoteScanDir)
