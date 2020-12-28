# #!/usr/bin/env python

# ### IMPORT MODULES ###
import re 
import urwid
import shlex
import struct
import numpy as np

### CUSTOM URWID EDIT ###
class SerialCommand(urwid.Edit):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['done', 'tab']
    # signals = ['tab']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self, self.get_edit_text())
            super(SerialCommand, self).set_edit_text('')
            return
        elif key == 'esc':
            super(SerialCommand, self).set_edit_text('')
            return
        elif key == 'tab':
            urwid.emit_signal(self, 'tab', self)
            return 

        urwid.Edit.keypress(self, size, key)

### CUSTOM URWID BUTTON ###
class TextOptionButton(urwid.WidgetWrap):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['click']

    def sizing(self):
        return frozenset([urwid.FLOW])

    def __init__(self, name, options, show_title=True, divider=True):
        # Variables
        self._current_idx = 0
        self._shown_idx = 0
        self._name = name
        self._options = options

        # Initialise urwid widgets
        curs_pos = len(max(options, key=len)) + 1 # to hide the cursor so don't see it flashing
        self._txt_title = urwid.Text(self._name, align='center')
        self._button_left = urwid.Text("<")
        self._button_right = urwid.Text(">")
        self._label = urwid.SelectableIcon(self._options[self._current_idx], curs_pos)
        self._label.set_align_mode("center")
        
        group = urwid.Columns([('fixed', 1, self._button_left), self._label, ('fixed', 1, self._button_right)], dividechars=1)
        group = urwid.AttrMap(group, None, focus_map='reversed')

        if show_title and divider:
            group = urwid.Pile([self._txt_title, group, urwid.Divider()])
        elif show_title:
            group = urwid.Pile([self._txt_title, group])
        elif divider:
            group = urwid.Pile([group, urwid.Divider()])
        self.__super.__init__(group)

        self.set_option(self._current_idx)

    def _repr_words(self):
        # include button.label in repr(button)
        return self.__super._repr_words() + [
            urwid.split_repr.python3_repr(self._name)]

    def set_name(self, name):
        self._name = name
        self._txt_title.set_text(name)

    def get_name(self):
        return self._name

    def set_option(self, idx):
        self._current_idx = idx
        self._shown_idx = idx
        self._label.set_text(self._options[idx])

    def get_option(self, shown=False):
        if shown:
            return self._shown_idx, self._options[self._current_idx]
        return self._current_idx, self._options[self._current_idx]

    def keypress(self, size, key):
        #  Change which option is currently shown
        if self._command_map[key] == urwid.CURSOR_LEFT:
            self._shown_idx = self._shown_idx - 1
            if self._shown_idx < 0:
                self._shown_idx = len(self._options)-1
            self._label.set_text(self._options[self._shown_idx])
        elif self._command_map[key] == urwid.CURSOR_RIGHT:
            self._shown_idx = (self._shown_idx + 1) % len(self._options)
            self._label.set_text(self._options[self._shown_idx])

        # Check to see if up/down arrow keypress
        # return keypress so parent widgets can deal with key (i.e. navigation)
        elif self._command_map[key] == urwid.CURSOR_DOWN or self._command_map[key] == urwid.CURSOR_UP:
            self.set_option(self._current_idx)
            return key

        # Escape reset
        elif key == 'esc':
            self.set_option(self._current_idx)

        # Set option to shown idx and emit click
        elif self._command_map[key] == urwid.ACTIVATE:
            self.set_option(self._shown_idx)
            self._emit('click')


        elif self._command_map[key] != urwid.ACTIVATE:
            return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not urwid.util.is_mouse_press(event):
            return False

        return True


class CustomListBox(urwid.ListBox):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['tab']

    def keypress(self, size, key):
        if key == 'tab':
            urwid.emit_signal(self, 'tab', self)
        urwid.ListBox.keypress(self, size, key)

### TERMINAL UI CLASS ###
class TerminalUI():
    """
    docstring
    """

    ### INITALISE ###
    def __init__(self):
        
        # CONSTANTS
        self.OPTIONS_WINDOW_WIDTH_WEIGHT = 0.3
        self.WRITE_DEBUG_LINES = 4

        # VARIABLES
        self.receive_text = urwid.Text("Received:")

        # Serial Receive Area
        receive_fill = urwid.Filler(self.receive_text, 'top')
        receive_box = urwid.LineBox(receive_fill)
        
        # Options Area
        options = {'Intepreter': (['Plain Text Interpreter', 'Smart Interpreter'], True, True), 'Option Two': (['a', 'b'], True, False), 'Option Three': (['c', 'd'], False, False), 'Option Four': (['e', 'f'], False, True)}

        body = [urwid.Text('OPTIONS', align='center'), urwid.Divider()]
        for key in options:
            button = TextOptionButton(key, options[key][0], options[key][1], options[key][2])
            urwid.connect_signal(button, 'click', self.OptionItemSelected)
            body.append(button)
        
        options_listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        # options_listbox = CustomListBox(urwid.SimpleFocusListWalker(body))
        options_box = urwid.LineBox(options_listbox)
        # return urwid.ListBox()

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
        frame = urwid.Frame(pile, urwid.Text("Terminal UI v0.1", align='center'))

        # Main Loop
        loop = urwid.MainLoop(frame, palette=[('reversed', 'standout', '')])

        # Connect Signals
        urwid.connect_signal(write_edit, 'done', self.OnCommandSerialEnter)  
        urwid.connect_signal(write_edit, 'tab', self.FocusChanged)
        urwid.connect_signal(options_listbox, 'tab', self.FocusChanged) 

        # Main Loop
        loop.run()

    def FocusChanged(self, widget):
        self.receive_text.set_text("Change Focus: " + str(widget))

        


    ### INITIALISE WINDOWS ###
    def InitialiseWindows(self):
        pass

    ### INITIALISE OPTIONS ###
    def InitialiseOptions(self, title, options):
        pass
        # body = [urwid.Text(title, align='center'), urwid.Divider()]
        # for key in options:
        #     button = TextOptionButton(key, options[key][0], options[key][1], options[key][2])
        #     urwid.connect_signal(button, 'click', self.OptionItemSelected)
        #     body.append(button)
        
        # return urwid.ListBox(urwid.SimpleFocusListWalker(body))


    def OptionItemSelected(self, button):
        self.receive_text.set_text("Done: " + str(button) + "\n" + "Shown: %d, Current: %d"%(button._shown_idx, button._current_idx))
        # response = urwid.Text([u'You chose ', choice, u'\n'])
        # done = urwid.Button(u'Ok')
        # urwid.connect_signal(done, 'click', exit_program)
        # main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map='reversed')]))

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

### INTEPRETERS ###
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
    
    # txt = input("Type something to test this out: ")
    # txt = '20.01 16 0b11 0x10 twenty twenty\ 20.01'
    # txt = 'blah\\\''
    # print("INTPUT: \"%s\""%(txt))
    # SmartCommandInterpreter(txt)
    terminal_ui = TerminalUI()

    # print(dir(urwid.Button))
    # print(dir(OptionsButton_2))