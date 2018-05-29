from sardana.macroserver.macro import Macro, macro, Type
import PyTango

@macro([["time", Type.Float, None, "time in seconds"] ])
def waittime(self, time):
    """Macro waittime"""
    acqConf = self.getEnv('acqConf')
    acqConf['waitTime'] = time
    self.setEnv('acqConf', acqConf)
    self.output("waittime set to %.2f s", time)
    

@macro([["ampl", Type.Float, None, "amplitude of mag. field in altOn scans [A]"],
        ["waittime", Type.Float, None, "waittime after magnet switching [s]"]])
def magnsettings(self, ampl, waittime):
    """Macro magnampl"""
    magnConf = self.getEnv('magnConf')
    magnConf['ampl'] = ampl
    magnConf['waitTime'] = waittime
    self.setEnv('magnConf', magnConf)
    self.output("magnampl set to %.2f A", ampl)    
    self.output("magnwaittime set to %.2f s", waittime)

    
@macro([["integ_time", Type.Float, None, "integration time"] ])
def ct_altOn(self, integ_time):
    
    mnt_grp_name = self.getEnv('ActiveMntGrp')
    mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)
        
    state, data = mnt_grp.count(integ_time)
    for ch_info in mnt_grp.getChannelsEnabledInfo():
        if ch_info.label == 'Pumped':
            PumpedFN = ch_info.full_name
        elif ch_info.label == 'Unpumped':
            UnpumpedFN = ch_info.full_name
        elif ch_info.label == 'PumpedErr':
            PumpedErrFN = ch_info.full_name
        elif ch_info.label == 'UnpumpedErr':
            UnpumpedErrFN = ch_info.full_name
        elif ch_info.label == 'Rel':
            RelFN = ch_info.full_name
        elif ch_info.label == 'RelS2S':
            RelS2SFN = ch_info.full_name
            
    storage = PyTango.DeviceProxy("moke/alton/1")
    storage["pumpedm"]      = data.get(PumpedFN)
    storage["unpumpedm"]    = data.get(UnpumpedFN)
    storage["pumpederrm"]   = data.get(PumpedErrFN)
    storage["unpumpederrm"] = data.get(UnpumpedErrFN)
    storage["relm"]         = data.get(RelFN)
    storage["rels2sm"]      = data.get(RelS2SFN)