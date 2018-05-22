from sardana.macroserver.macro import Macro, macro, Type

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
