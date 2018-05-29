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
    ct, _ = self.createMacro('ct',  integ_time)
    # createMacro returns a tuple composed from a macro object
    # and the result of the Macro.prepare method
    self.runMacro(ct)
    
    pumped = 'tango://epics-archiver.hhg.lab:10000/expchan/zhictrl/0'
    unpumped = 'tango://epics-archiver.hhg.lab:10000/expchan/zhictrl/1'
    
    data = ct.getData()
#    self.info(data.data[pumped])
#    self.info(data.data[unpumped])
    
    storage = PyTango.DeviceProxy("moke/alt_on_counter/1")
    storage["pumpedm"]   = data.data[pumped]
    storage["unpumpedm"] = data.data[unpumped]
    
#    for idx, rc in data.items():
#        self.info("Record Data for record No: %r" %(idx))
#        for counter, value in rc.data.items():
#            self.info("Counter %r: %r" % (counter, value))
