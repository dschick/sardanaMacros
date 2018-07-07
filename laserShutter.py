from epics import caget, caput
import time

from sardana.macroserver.macro import macro

@macro()
def laseron(self):
    """Macro laserOn"""
    pvPrefix = 'SHUTTER:NOPA:'
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
    pvPrefix = 'SHUTTER:NOPA:'
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
    pvPrefix = 'SHUTTER:MOKE:'
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
    pvPrefix = 'SHUTTER:MOKE:'
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