from sardana.macroserver.macro import macro, Type

@macro()
def alton(self):
    """Macro alton"""
    acqConf = self.getEnv('acqConf')
    acqConf['altOn'] = True
    self.setEnv('acqConf', acqConf)
    self.info('switching alternate ON')
    
    # enable minus field counters
    mnt_grp = self.getObj(self.getEnv('ActiveMntGrp'), type_class=Type.MeasurementGroup)
    mnt_grp.enableChannels(['spec1M',
                            'spec2M',
                            'spec3M',
                            'spec4M',
                            'spec5M',
                            'spec6M',
                            'spec7M',
                            'spec8M',
                            'spec9M',
                            'spec10M',
                            'ref1M',
                            'ref2M',
                            'ref3M',
                            'ref4M',
                            'ref5M',
                            'ref6M',
                            'ref7M',
                            'ref8M',
                            'ref9M',
                            'ref10M',
                            'rel1M',
                            'rel2M',
                            'rel3M',
                            'rel4M',
                            'rel5M',
                            'rel6M',
                            'rel7M',
                            'rel8M',
                            'rel9M',
                            'rel10M',
                            'fileIDM',
                            'thorlabsPMM',
                            'keithleyAM',
                            'keithleyVM',
                            'epochM',])

@macro()    
def altoff(self):
    """Macro altoff"""
    acqConf = self.getEnv('acqConf')
    acqConf['altOn'] = False
    self.setEnv('acqConf', acqConf)
    self.info('switching alternate OFF')
    
    # disable minus field counters
    mnt_grp = self.getObj(self.getEnv('ActiveMntGrp'), type_class=Type.MeasurementGroup)
    mnt_grp.disableChannels(['spec1M',
                            'spec2M',
                            'spec3M',
                            'spec4M',
                            'spec5M',
                            'spec6M',
                            'spec7M',
                            'spec8M',
                            'spec9M',
                            'spec10M',
                            'ref1M',
                            'ref2M',
                            'ref3M',
                            'ref4M',
                            'ref5M',
                            'ref6M',
                            'ref7M',
                            'ref8M',
                            'ref9M',
                            'ref10M',
                            'rel1M',
                            'rel2M',
                            'rel3M',
                            'rel4M',
                            'rel5M',
                            'rel6M',
                            'rel7M',
                            'rel8M',
                            'rel9M',
                            'rel10M',
                            'fileIDM',
                            'thorlabsPMM',
                            'keithleyAM',
                            'keithleyVM',
                            'epochM',])