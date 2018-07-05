from sardana.macroserver.macro import imacro, macro, Type
import PyTango
import numpy as np

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

@imacro()
def fluenceconf(self):
    fluencePM = PyTango.DeviceProxy("pm/fluencectrl/1")
    try:
        lastPumpHor = fluencePM.pumpHor
        lastPumpVer = fluencePM.pumpVer
        lastRefl    = fluencePM.refl
        lastRepRate = fluencePM.repRate
    except:
        lastPumpHor = 100
        lastPumpVer = 100
        lastRefl    = 0
        lastRepRate = 3000
        
    
    
    label, unit = "hor", "um"
    pumpHor = self.input("What is the horizontal beam diameter (FWHM)?", data_type=Type.Float,
                      title="Horizontal beam diameter", key=label, unit=unit,
                      default_value=lastPumpHor, minimum=0.0, maximum=100000)
    label, unit = "ver", "um"
    pumpVer = self.input("What is the vertical beam diameter (FWHM)?", data_type=Type.Float,
                      title="Vertical beam diameter", key=label, unit=unit,
                      default_value=lastPumpVer, minimum=0.0, maximum=100000)
    label, unit = "refl", "%"
    refl = self.input("What is the sample reflectivity?", data_type=Type.Float,
                      title="Sample reflectivity", key=label, unit=unit,
                      default_value=lastRefl, minimum=0.0, maximum=100)
    label, unit = "repRate", "Hz"
    repRate = self.input("What is the laser repetition rate?", data_type=Type.Float,
                      title="Laser repetition rate", key=label, unit=unit,
                      default_value=lastRepRate, minimum=0.0, maximum=10000)
        
    fluencePM.pumpHor = pumpHor
    fluencePM.pumpVer = pumpVer
    fluencePM.refl    = refl
    fluencePM.repRate = repRate
    
    self.output("Settings:")
    self.output("pumpHor: %.2f um", pumpHor)
    self.output("pumpVer: %.2f um", pumpVer)
    self.output("refl   : %.2f %%", refl)
    self.output("repRate: %.2f Hz", repRate)
    
    power = self.getPseudoMotor("power")
    fluence = self.getPseudoMotor("fluence")
    minPower, maxPower = power.getPositionObj().getLimits()
    
    trans   = 1-(refl/100)
    minFluence = minPower*trans/(repRate/1000*np.pi*pumpHor/10000/2*pumpVer/10000/2)
    maxFluence = maxPower*trans/(repRate/1000*np.pi*pumpHor/10000/2*pumpVer/10000/2)
    
    self.output('Setting fluence limits using current power limits:')
    fluence.getPositionObj().setLimits(minFluence,maxFluence)
    self.output("minimum fluence %.3f mJ/cm^2", minFluence)
    self.output("maximum fluence %.3f mJ/cm^2", maxFluence)  
    

@macro([["P0", Type.Float, None, "P0"],
        ["Pm", Type.Float, None, "Pm"],
        ["offset", Type.Float, None, "offset"],
        ["period", Type.Float, None, "period"]])
def setPowerParameter(self, P0, Pm, offset, period):
    """This sets the parameters of the power pseudo motor"""
    
    power = PyTango.DeviceProxy("pm/powerctrl/1")
    self.info('Update parameters of pseudo motor power')
    power.offset = offset
    power.period = period
    power.P0     = P0
    power.Pm     = Pm

   