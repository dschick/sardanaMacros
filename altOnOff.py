from sardana.macroserver.macro import Macro, macro, Type
import PyTango
import numpy as np
@macro()
def altOn(self):
    """Macro altOn"""
    acqConf = self.getEnv('acqConf')
    acqConf['altOn'] = True
    self.setEnv('acqConf', acqConf)
    self.info('switching altOn')

@macro()    
def altOff(self):
    """Macro altOff"""
    acqConf = self.getEnv('acqConf')
    acqConf['altOn'] = False
    self.setEnv('acqConf', acqConf)
    self.info('switching altOff')
    
    # setting all M-counter to 0
    storage = PyTango.DeviceProxy("moke/alton/1")
    storage["pumpedm"]      = 0
    storage["unpumpedm"]    = 0
    storage["pumpederrm"]   = 0
    storage["unpumpederrm"] = 0
    storage["relm"]         = 0
    storage["rels2sm"]      = 0
    