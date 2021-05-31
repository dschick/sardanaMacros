from sardana.macroserver.macro import imacro, Macro, macro, Type, Optional, \
ParamRepeat
import PyTango
import numpy as np
    
@imacro()
def acqconf(self):
    # run all the other configuration
    acqConf = self.getEnv('acqConf')
    label, unit = "Alternate On/Off", ""
    alt_on = self.input("Alternate Mode On/Off?", data_type=Type.Boolean,
                      title="Alternate Mode", key=label, unit=unit,
                      default_value=acqConf['altOn'], minimum=0.0, maximum=100)
    
    acqConf['altOn'] = alt_on
    self.setEnv('acqConf', acqConf)
    
    self.execMacro('waittime')
    self.execMacro('magnconf')
    self.execMacro('powerconf')    
    self.execMacro('fluenceconf')
    self.output('\r')
    self.execMacro('acqrep')

@macro()
def acqrep(self):
    acqConf = self.getEnv('acqConf')
    self.output('Gen. Settings   : %s | Waittime = %.2f s', 
                ('Alt ON' if acqConf['altOn'] else 'Alt OFF'),
                acqConf['waitTime'])
    self.execMacro('magnrep')
    self.execMacro('powerrep')
    self.execMacro('fluencerep')

@imacro([["time", Type.Float, Optional, "time in seconds"] ])
def waittime(self, time):
    """Macro waittime"""
    acqConf = self.getEnv('acqConf')
    if time is None:
        label, unit = "Waittime", "s"
        time = self.input("Wait time before every acqisition?", 
                          data_type=Type.Float,
                          title="Waittime Amplitude", key=label, unit=unit,
                          default_value=acqConf['waitTime'], minimum=0.0, 
                          maximum=100)
    
    acqConf['waitTime'] = time
    self.setEnv('acqConf', acqConf)
    self.output("waittime set to %.2f s", time)
    

@imacro([
        ["ampl", Type.Float, Optional, 
          "amplitude of mag. field in altOn scans [A]"],
        ["waittime", Type.Float, Optional, 
         "waittime after magnet switching [s]"]
        ])
def magnconf(self, ampl, waittime):
    """Macro magnampl"""
    magnConf = self.getEnv('magnConf')    
    
    if ampl is None:
        label, unit = "Amplitude", "A"
        ampl = self.input("Set magnet amplitude:", data_type=Type.Float,
                          title="Magnet Amplitude", key=label, unit=unit,
                          default_value=magnConf['ampl'], minimum=0.0, 
                          maximum=10)
    
    if waittime is None:
        label, unit = "Waittime", "s"
        waittime = self.input("Set magnet waittime:", data_type=Type.Float,
                          title="Magnet Waittime", key=label, unit=unit,
                          default_value=magnConf['waitTime'], minimum=0.0, 
                          maximum=100)
    
    
    magnConf['ampl']     = ampl
    magnConf['waitTime'] = waittime
    self.setEnv('magnConf', magnConf)
    self.execMacro('magnrep')

@macro()
def magnrep(self):
    # return all magnconf values
    magnConf = self.getEnv('magnConf')
    self.output('Magnet Settings : magn. amplitude = %.2f A | '
                'magn. waittime = %.2f s', 
                magnConf['ampl'], magnConf['waitTime'])

@macro()
def magnon(self):
    self.execMacro('send2ctrl caenfastpsctrl MON')
    self.output('Magnet output switched ON')

@macro()
def magnoff(self):
    self.execMacro('send2ctrl caenfastpsctrl MOFF')
    self.output('Magnet output switched OFF')

@imacro([["pumpHor", Type.Float, Optional, "pumpHor"],
        ["pumpVer", Type.Float, Optional, "pumpVer"],
        ["refl", Type.Float, Optional, "reflectivity"],
        ["repRate", Type.Float, Optional, "repetition rate"]])
def fluenceconf(self, pumpHor, pumpVer, refl, repRate):
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
    
    if pumpHor is None:    
        label, unit = "hor", "um"
        pumpHor = self.input("Set the horizontal beam diameter (FWHM):", 
                             data_type=Type.Float,
                             title="Horizontal beam diameter", key=label, 
                             unit=unit, default_value=lastPumpHor, minimum=0.0,
                             maximum=100000)
    if pumpVer is None: 
        label, unit = "ver", "um"
        pumpVer = self.input("Set the vertical beam diameter (FWHM):", 
                             data_type=Type.Float, 
                             title="Vertical beam diameter", key=label,
                             unit=unit, default_value=lastPumpVer, minimum=0.0,
                             maximum=100000)
    if refl is None:
        label, unit = "refl", "%"
        refl = self.input("Set the sample reflectivity:", data_type=Type.Float,
                          title="Sample reflectivity", key=label, unit=unit,
                          default_value=lastRefl, minimum=0.0, maximum=100)
    if repRate is None:       
        label, unit = "repRate", "Hz"
        repRate = self.input("Set the laser repetition rate:", 
                             data_type=Type.Float,
                             title="Laser repetition rate", key=label, 
                             unit=unit, default_value=lastRepRate, minimum=0.0,
                             maximum=10000)
        
    fluencePM.pumpHor = pumpHor
    fluencePM.pumpVer = pumpVer
    fluencePM.refl    = refl
    fluencePM.repRate = repRate
        
    power = self.getPseudoMotor("power")
    fluence = self.getPseudoMotor("fluence")
    minPower, maxPower = power.getPositionObj().getLimits()
    
    trans   = 1-(refl/100)
    minFluence = minPower*trans/(
                    repRate/1000*np.pi*pumpHor/10000/2*pumpVer/10000/2)
    maxFluence = maxPower*trans/(
                    repRate/1000*np.pi*pumpHor/10000/2*pumpVer/10000/2)
    self.info('Update limits of pseudo motor fluence')
    fluence.getPositionObj().setLimits(minFluence, maxFluence)
    
    self.execMacro('fluencerep')


@macro()
def fluencerep(self):
    fluencePM = PyTango.DeviceProxy("pm/fluencectrl/1")
    
    pumpHor = fluencePM.pumpHor
    pumpVer = fluencePM.pumpVer
    refl    = fluencePM.refl
    repRate = fluencePM.repRate
    
    self.output('Fluence Settings: pumpHor = %.2f um | pumpVer = %.2f um | '
                'refl = %.2f %% | repRate = %.2f Hz', 
                pumpHor, pumpVer, refl, repRate)
    
    fluence = self.getPseudoMotor("fluence")
    [minFluence, maxFluence] = fluence.getPositionObj().getLimits()
    
    self.output('Fluence Limits  : min = %.3f mJ/cm^2 | max = %.3f mJ/cm^2', 
                minFluence, maxFluence)
        

@imacro([["P0", Type.Float, Optional, "P0"],
        ["Pm", Type.Float, Optional, "Pm"],
        ["offset", Type.Float, Optional, "offset"],
        ["period", Type.Float, Optional, "period"]])
def powerconf(self, P0, Pm, offset, period):
    """This sets the parameters of the power pseudo motor"""
    power = PyTango.DeviceProxy("pm/powerctrl/1")
    
    if P0 is None:    
        label, unit = "P0", "W"
        P0 = self.input("Set the minimum power:", data_type=Type.Float,
                          title="Minimum Power", key=label, unit=unit,
                          default_value=power.P0, minimum=0.0, maximum=100000)
    
    if Pm is None:    
        label, unit = "Pm", "W"
        Pm = self.input("Set the maximum power:", data_type=Type.Float,
                          title="Maximum Power", key=label, unit=unit,
                          default_value=power.Pm, minimum=0.0, maximum=100000)
    
    if offset is None:    
        label, unit = "offset", "deg"
        offset = self.input("Set the radial offset:", data_type=Type.Float,
                          title="Radial Offset", key=label, unit=unit,
                          default_value=power.offset, minimum=-45, maximum=45)
        
    if period is None:    
        label, unit = "period", ""
        period = self.input("Set the radial period:", data_type=Type.Float,
                          title="Radial Period", key=label, unit=unit,
                          default_value=power.period, minimum=0, maximum=2)
    
    
    self.info('Update parameters of pseudo motor power')
    power.offset = offset
    power.period = period
    power.P0     = P0
    power.Pm     = Pm
    
    self.execMacro('set_lim', 'power', P0, (Pm+P0))    
    self.execMacro('powerrep')

@macro()
def powerrep(self):
    # return all powerconf values
    power = PyTango.DeviceProxy("pm/powerctrl/1")
    self.output('Power Settings  : P0 = %.4f W | Pm = %.4f W | '
                'offset = %.2f deg | period = %.2f', 
                power.P0, power.Pm, power.offset, power.period)

class plotselect(Macro):
    """
    plotselect counter1 counter2 ... (change plot display of active measurement
    group)
    """
    param_def = [
          ['plotChs', ParamRepeat(
                  ['plotChs', Type.String, 'None', ""], min=0), None, ""]
     ]

    def run(self, plotChs):
        mntGrp = self.getEnv('ActiveMntGrp')
        self.mntGrp = self.getObj(mntGrp, type_class=Type.MeasurementGroup)
        cfg = self.mntGrp.getConfiguration()
        channels = self.mntGrp.getChannels()
        channelNames = []

        # Enable Plot only in the channels passed.
        for channel in channels:
            if channel['enabled']:
                channelNames.append(channel['name'])
                if channel['name'] in plotChs:
                    # Enable Plot
                    self.info("Plot channel %s" % channel['name'])
                    channel['plot_type'] = 1
                    channel['plot_axes'] = ['<mov>']
                else:
                    # Disable Plot
                    channel['plot_type'] = 0
                    channel['plot_axes'] = []

        # check if plotChs exists
        for plotCh in plotChs:
            if plotCh not in channelNames:
                self.warning('channel %s is not enabled or does not exist in'
                             ' the current measurement group' % plotCh)

        # Force set Configuration.
        self.mntGrp.setConfiguration(cfg.raw_data)
