__all__ = ["wpCalibScan", "setPowerParameter"]

__docformat__ = 'restructuredtext'

import numpy
import lmfit
import PyTango

from sardana.macroserver.macro import *
from sardana.macroserver.scan import *

@macro()
def wpCalibScan(self):
    """This runs a waveplate calibration scan"""

    acqConf = self.getEnv('acqConf')
    oldWaitTime = acqConf['waitTime']
    newWaitTime = 1
    
    counter = 'tango://epics-archiver.hhg.lab:10000/expchan/epicszctrl/1'
    motor   = 'wp'
    
    self.execMacro('waittime', newWaitTime)
    self.execMacro('altOff')
    self.execMacro('pumpOff')   
        
    ret = self.createMacro('ascan', 'wp', '-5', '55', '60', '1')
    # createMacro returns a tuple composed from a macro object
    # and the result of the Macro.prepare method
    my_scan, _ = ret
    self.runMacro(my_scan)    
    
    self.execMacro('waittime', oldWaitTime)
    
    data = my_scan.data
    
    wp = []
    pm = []
    
    for i in range(len(data)):
        pm.append(data.records[i].data[counter])
        wp.append(data.records[i].data[motor])
    
    mod = lmfit.Model(sinSqrd)
    par = lmfit.Parameters()
    
    par.add('Pm',     value=.5, vary=True, min=0)
    par.add('P0',     value=0, vary=True)
    par.add('offset', value=0, vary=True)
    par.add('period', value=1, vary=True, min = 0.9, max = 1.1)

    out = mod.fit(pm, par, x=wp)
    
    self.info(out.best_values)    
    
    self.pyplot.plot(wp, pm, 'o', label='data') #
    self.pyplot.plot(wp, out.best_fit, label='fit')
    self.pyplot.title(r'Fit data by $P(wp) = P_m*(sin((wp-offset)*2/180*\pi*period)^2+P_0)$')
    self.pyplot.xlabel('wp angle [deg.]')
    self.pyplot.xlabel('laser power [W]')
    self.pyplot.legend()
    
    self.execMacro('setPowerParameter', out.best_values['P0'], out.best_values['Pm'], out.best_values['offset'], out.best_values['period'])
    
    
def sinSqrd(x,Pm,P0,offset,period):
    return Pm*(numpy.sin((x-offset)*2/180.*numpy.pi*period)**2) + P0


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
    