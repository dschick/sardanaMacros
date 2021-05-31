from epics import caget, caput
import time

from sardana.macroserver.macro import macro

@macro()
def laseron(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:PM:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Open":
        self.output("Laser shutter already open")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Open":
            self.output("Laser shutter opened")
        else:
            self.output("Could not open Laser shutter")

@macro()
def laseroff(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:PM:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Closed":
        self.output("Laser shutter already closed")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Closed":
            self.output("Laser shutter closed")
        else:
            self.output("Could not close Laser shutter")

@macro()
def pumpon(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHGPUMP:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Open":
        self.output("Pump shutter already open")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Open":
            self.output("Pump shutter opened")
        else:
            self.output("Could not open Pump shutter")

@macro()
def pumpoff(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHGPUMP:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Closed":
        self.output("Pump shutter already closed")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Closed":
            self.output("Pump shutter closed")
        else:
            self.output("Could not close Pump shutter")

@macro()
def probeon(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHG:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Open":
        self.output("Probe shutter already open")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Open":
            self.output("Probe shutter opened")
        else:
            self.output("Could not open probe shutter")

@macro()
def probeoff(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHG:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Closed":
        self.output("Probe shutter already closed")
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Closed":
            self.output("Probe shutter closed")
            if caget('HHG:GASCELL:pidEnabled') == 1:
                self.output("Gas is still on!!")
            else:
                self.output("Gas is already off")
        else:
            self.output("Could not close Probe shutter")
            
            
@macro()
def hhgon(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHG:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Open":
        self.output("Probe shutter already open")
        caput('HHG:GASCELL:pidEnabled', 1)
        self.output("Gas enabled")        
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Open":
            self.output("Probe shutter opened")
            caput('HHG:GASCELL:pidEnabled', 1)
            self.output("Gas enabled")  
        else:
            self.output("Could not open probe shutter")
            self.output("Gas has not been enabled")
            

@macro()
def hhgoff(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:HHG:'
    shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
    if shutterState == "Closed":
        self.output("Probe shutter already closed")
        caput('HHG:GASCELL:pidEnabled', 0)
        self.output("Gas disabled") 
    else:
        caput(pvPrefix + 'Flip', 3)
        time.sleep(1)
        shutterState = caget(pvPrefix + 'Shutter_RBV', as_string=True)
        if shutterState == "Closed":
            self.output("Probe shutter closed")
            caput('HHG:GASCELL:pidEnabled', 0)
            self.output("Gas disabled") 
        else:
            self.output("Could not close Probe shutter")
            caput('HHG:GASCELL:pidEnabled', 0)
            self.output("Gas disabled anyway") 
            

@macro()
def gason(self):
    caput('HHG:GASCELL:pidEnabled', 1)
    self.output("Gas enabled") 

@macro()
def gasoff(self):
    caput('HHG:GASCELL:pidEnabled', 0)
    self.output("Gas disabled")     
    
            