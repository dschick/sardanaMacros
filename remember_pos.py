from sardana.macroserver.macro import imacro, macro, Macro, Type, Optional, ParamRepeat
import PyTango
import numpy as np




@macro([
            ["name", Type.String, Optional, "Save positions"],
            ["motor_list", [["moveable", Type.Moveable, None, "moveable to get position"]],None, "list of moveables to get positions"] #list of movables with n entries

]) 

def remember_pos(self, name, motor_list):
    positions = {}    #create dict
    for motor in motor_list:
        positions[str(motor)] = motor.getPosition()
    self.setEnv(name, positions)




@macro([
        ["name", Type.String, Optional, "Recall saved positions"],
        ])
def recall_pos(self, name):
    positions = self.getEnv(name)
    for key, value in positions.items():    
        self.output("%s @ %.4f",key, value)




@macro([
        ["name", Type.String, Optional, "Move to saved positions"],
        ])
def restore_pos(self, name):
    positions = self.getEnv(name)
    for key, value in positions.items():    
        self.output("%s @ %.4f",key, value)
        self.execMacro('umv', key, value)




