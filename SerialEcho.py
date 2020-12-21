# #!/usr/bin/env python

# ### IMPORT MODULES ###
import re 
import urwid
import shlex
import struct
import numpy as np


class SerialCommand(urwid.Edit):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['done']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self, self.get_edit_text())
            super(SerialCommand, self).set_edit_text('')
            return
        elif key == 'esc':
            super(SerialCommand, self).set_edit_text('')
            return
        urwid.Edit.keypress(self, size, key)


### TERMINAL UI CLASS ###
class TerminalUI():
    """
    docstring
    """

    ### INITALISE ###
    def __init__(self):
        
        # CONSTANTS
        self.OPTIONS_WINDOW_WIDTH_WEIGHT = 0.2
        self.WRITE_DEBUG_LINES = 4

        # VARIABLES
        self.receive_text = urwid.Text("Received:")

        # Serial Receive Area
        receive_fill = urwid.Filler(self.receive_text, 'top')
        receive_box = urwid.LineBox(receive_fill)
        
        # Options Area
        options_text = urwid.Text("Options:")
        options_fill = urwid.Filler(options_text, 'top')
        options_box = urwid.LineBox(options_fill)

        # Serial Send Area
        write_edit = SerialCommand(">>")
        write_fill = urwid.Filler(write_edit, 'top', min_height=1)
        self.write_edit_debug = urwid.Text('')
        write_fill_debug =urwid.Filler(self.write_edit_debug, 'top', min_height=self.WRITE_DEBUG_LINES)
        write_pile = urwid.Pile([write_fill, (self.WRITE_DEBUG_LINES, write_fill_debug)])
        write_box = urwid.LineBox(write_pile)

        # Screen
        column = urwid.Columns([('weight', 1-self.OPTIONS_WINDOW_WIDTH_WEIGHT, receive_box), ('weight', self.OPTIONS_WINDOW_WIDTH_WEIGHT, options_box)])
        pile = urwid.Pile([column, (self.WRITE_DEBUG_LINES+3, write_box)]) # +3, 2 for border, 1 for edit text row
        frame = urwid.Frame(pile, urwid.Text("Serial Echo v0.1", align='center'))
        loop = urwid.MainLoop(frame)

        # Connect Signals
        urwid.connect_signal(write_edit, 'done', self.OnCommandSerialEnter)

        # Main Loop
        loop.run()


    ### INITIALISE WINDOWS ###
    def InitialiseWindows(self):
        pass

    ### SERIAL COMMAND ENTERED ###
    def OnCommandSerialEnter(self, widget, command):
        self.receive_text.set_text("Entered: " + command)

        if command[0] == 'r':
            command_hex = SmartCommandInterpreter(command[1:])

        elif command[0] == 'w' or (command[0] != 'r'):
            if command[0] == 'w':
                command = command[1:]
            command_hex = SmartCommandInterpreter(command)
            # command_hex[0] = command_hex[0] | (1<<7)


        hex_string = "".join(" 0x%02x"%(x) for x in command_hex)
        self.write_edit_debug.set_text("Input (raw): %s\nInput (hex):%s"%(command, hex_string))

    
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
    for idx, val in enumerate(split_command):
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

    # print(retval)
    # print("".join(" 0x%02x"%(x) for x in retval))
    return retval

        

# 20.01 20 0b11 0x11 twenty twenty\ 20.01

### MAIN FUNCTION ###

if __name__ == "__main__":
    
    # txt = input("Type something to test this out: ")
    # txt = '20.01 16 0b11 0x10 twenty twenty\ 20.01'
    # txt = 'blah\\\''
    # print("INTPUT: \"%s\""%(txt))
    # SmartCommandInterpreter(txt)
    terminal_ui = TerminalUI()