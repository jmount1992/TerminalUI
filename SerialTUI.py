#!/usr/bin/env python3

### IMPORT MODULES ###
import re
import shlex
import serial
import serial.tools.list_ports
from TerminalUI import TerminalUI

#################
### FUNCTIONS ###
#################

### TERMINAL UI CALLBACKS ###
def CommandEntered(terminal_ui : TerminalUI, command):
    terminal_ui.SetCommandDebugText(" Debug: %s"%(command))


def OptionItemSelected(terminal_ui : TerminalUI, name : str, option_index : int, option_string : str):

    if name == 'write_debug':
        if option_string == 'On':
            terminal_ui.CommandDebugTextVisible(True)
        else:
            terminal_ui.CommandDebugTextVisible(False)

### INTERPRETERS ###
def PlainTextInterpreter(command):
    # Simply convert string into bytearray
    retval = bytearray([ord(x) for x in command])
    return retval

def SmartCommandInterpreter(command):
    # Portions within quotation marks will be considered a string and interpeted as such, preserving spaces
    # Continuous portions consisting of both letters and number will be considered a string (i.e. 2ab will be encoded as [50, 97, 98] in ASCII)
    # Spaces between items will be considered seperators and will not be encoded (i.e. 2ab 1ab will be encoded as [50, 97, 98, 50, 97, 98])
    # To ignore a space use backslash an a escape character (i.e. 2ab\ 2ab\\ will be encoded as [50, 97, 98, 32, 50, 97, 98, 92])
    # Portions consisting only of numbers will be considered integers.
    # Continuous number portions prepended by a 0b or 0x prefix will be considered binary or hex respectively.

    retval = bytearray()

    # Split on spaces, except with those preceded by a backslash
    split_command = shlex.split(command)
    for val in slit_command:
        # Check portion type
        if re.match('^[0-9]*$', val):
            # integer
            retval.append(int(val))

        elif re.match('^[0-9\.]*$', val):
            # float - encoded as four bytes
            for x in struct.pack('f', float(val)):
                retval.append(x)
                
        elif re.match('0[bB][0-9a-fA-F]+', val):
            # binary
            retval.append(int(val, 2))

        elif re.match('0[xX][0-9a-fA-F]+', val):
            # hex
            retval.append(int(val, 16))
        
        else:
            # string
            for x in val:
                retval.append(ord(x)) # convert from character into integer representation
    
    # return command as bytearray
    return retval


### MAIN FUNCTION ###
if __name__ == "__main__":

    # Serial Emulator
    # emulator = SerialEmulator('./ttydevice','./ttyclient')

    # Serial Devices List
    # comports = serial.Serial
    # print([comport.device for comport in serial.tools.list_ports.comports()])
    comport_names = [comport.device for comport in serial.tools.list_ports.comports()]

    # Options
    options = {}
    options['Serial Connection'] = ({'com_port': comport_names, 'baud_rate': ['9600', '52600'], 'connect': ['open']}, True, True)
    options['Command Intepreter'] = ({'cmd_interpreter': ['Plain Text Interpreter', 'Smart Intepreter']}, True, True)
    options['Write Debug'] = ({'write_debug': ['On', 'Off']}, True, True)

    # Terminal UI 
    terminal_ui = TerminalUI('Serial Echo v0.1', CommandEntered, options, OptionItemSelected)
    terminal_ui.Run()