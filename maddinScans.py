from sardana.macroserver.macro import Macro, macro, Type
import numpy as np

@macro()
def fluenceDelayScan20180523(self):
    """Macro fluenceDelayScan20180523"""
    self.output("Running fluenceDelayScan20180523...")

    wpAngles = np.r_[5:46:5]
    kepco = self.getMotor("kepco")
    wp = self.getMotor("wp")
    magCurr = 40    
    
    self.execMacro('laserOn')
    self.execMacro('pumpOn')
    self.execMacro('waittime 0')
    
    for wpAngle in wpAngles:
        self.output(wpAngle)
        
        wp.move(wpAngle)
        
        kepco.move(-1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        kepco.move(1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        
        kepco.move(-1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        kepco.move(1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        
    self.execMacro('pumpOff')
    self.execMacro('waittime 1')
    self.execMacro('ascan wp -5 55 60 1')
    self.execMacro('laserOff')

@macro()    
def fluenceDelayScan20180525(self):
    """Macro fluenceDelayScan20180525"""
    self.output("Running fluenceDelayScan20180525...")

    wpAngles = np.r_[6,9.65,12.35,14.58,16.69,18.69,20.5,22.4,24.34,26,27.9,29.95,32.25,34.84,38,45]
    kepco = self.getMotor("kepco")
    wp = self.getMotor("wp")
    magCurr = 40    
    
    self.execMacro('laserOn')
    self.execMacro('pumpOn')
    self.execMacro('waittime 0')
    
    for wpAngle in wpAngles:
        self.output(wpAngle)
        
        wp.move(wpAngle)
        
        kepco.move(-1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        kepco.move(1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        
        kepco.move(-1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        kepco.move(1*magCurr)
        self.execMacro('regscan delay 1 -830 -825 5 -824.5 5 -823.8 35 -822 18 -820 10 -800 20 1000 18')
        
    self.execMacro('pumpOff')
    self.execMacro('waittime 1')
    self.execMacro('ascan wp -5 55 60 1')
    self.execMacro('laserOff')
    self.execMacro('laserOff')