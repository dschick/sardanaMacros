from sardana.macroserver.macro import imacro, macro, Macro, Type, Optional, ParamRepeat
import sys
import time


#@macro([
#            ["seconds", Type., Optional, "Save positions"],
#           
#
#]) 
#
#def stopwatch(self, name, motor_list):
#    positions = {}    #create dict
#    for motor in motor_list:
#        positions[str(motor)] = motor.getPosition()
#    self.setEnv(name, positions)
