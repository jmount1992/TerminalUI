#!/usr/bin/env python

# ### IMPORT MODULES ###
import re 
import urwid
import shlex
import struct
import numpy as np

### CUSTOM URWID EDIT ###
class CommandEdit(urwid.Edit):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['done']

    def __init__(self, caption=u"", edit_text=u"", multiline=False, align=urwid.LEFT, wrap=urwid.SPACE, allow_tab=False, edit_pos=None, layout=None, mask=None, history_size=50):

        self._history = []
        self._history_idx = -1
        self._history_size = history_size

        # Run standard urwid.Edit init
        urwid.Edit.__init__(self, caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)

    def keypress(self, size, key):

        # Curser Up to go back in history
        if self._command_map[key] == urwid.CURSOR_UP:
            self._history_idx = min(self._history_idx+1, len(self._history)-1)
            self.set_edit_text(self._history[self._history_idx])
            return

        # Cursor Down to go forward in history
        if self._command_map[key] == urwid.CURSOR_DOWN:
            self._history_idx = max(self._history_idx-1, -1)
            if self._history_idx == -1:
                self.set_edit_text('')
            else:
                self.set_edit_text(self._history[self._history_idx])
            return

        # Enter to emit done signal
        elif key == 'enter':
            self._history.insert(0, self.get_edit_text()) 
            if len(self._history) > self._history_size:
                self._history.pop()
            self._history_idx = -1

            urwid.emit_signal(self, 'done', self, self.get_edit_text())
            self.set_edit_text('')
            # super(SerialCommand, self).set_edit_text('')
            return

        # Escape to clear text
        elif key == 'esc':
            self._history_idx = -1
            self.set_edit_text('')
            # super(SerialCommand, self).set_edit_text('')
            return

        urwid.Edit.keypress(self, size, key)


### CUSTOM URWID BUTTON ###
class TextOptionButton(urwid.WidgetWrap):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['change']

    def sizing(self):
        return frozenset([urwid.FLOW])

    def __init__(self, name, options, enabled=True, reset_focus_lost=True, enter_for_change=True):
        # Variables
        self._current_idx = 0
        self._shown_idx = 0
        self._name = name
        self._options = options
        self._enabled = enabled
        self._reset_after_lost_focus = reset_focus_lost
        self._enter_fire_change_event = enter_for_change

        # Initialise urwid widgets
        curs_pos = len(max(options, key=len)) + 1 # to hide the cursor so don't see it flashing
        self._button_left = urwid.Text("<")
        self._button_right = urwid.Text(">")
        self._label = urwid.SelectableIcon(self._options[self._current_idx], curs_pos)
        self._label.set_align_mode("center")
        
        button = urwid.Columns([('fixed', 1, self._button_left), self._label, ('fixed', 1, self._button_right)], dividechars=1)
        button = urwid.AttrMap(button, None, focus_map='reversed')
        self.__super.__init__(button)

        self.set_option(self._current_idx)

    def _repr_words(self):
        # include button.label in repr(button)
        return self.__super._repr_words() + [
            urwid.split_repr.python3_repr(self._name)]

    def set_name(self, name):
        self._name = name

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
        if self._command_map[key] == urwid.CURSOR_LEFT or self._command_map[key] == urwid.CURSOR_RIGHT:
            if self._command_map[key] == urwid.CURSOR_LEFT:
                self._shown_idx = self._shown_idx - 1
                if self._shown_idx < 0:
                    self._shown_idx = len(self._options)-1
                self._label.set_text(self._options[self._shown_idx])
            elif self._command_map[key] == urwid.CURSOR_RIGHT:
                self._shown_idx = (self._shown_idx + 1) % len(self._options)
                self._label.set_text(self._options[self._shown_idx])
            
            if not self._enter_fire_change_event:
                self.set_option(self._shown_idx)
                self._emit('change')


        # Check to see if up/down arrow keypress
        # return keypress so parent widgets can deal with key (i.e. navigation)
        elif self._reset_after_lost_focus and (self._command_map[key] == urwid.CURSOR_DOWN or self._command_map[key] == urwid.CURSOR_UP):
            self.set_option(self._current_idx)
            return key

        # Escape reset
        elif key == 'esc':
            self.set_option(self._current_idx)

        # Set option to shown idx and emit click
        elif self._enter_fire_change_event and self._command_map[key] == urwid.ACTIVATE:
            self.set_option(self._shown_idx)
            self._emit('change')


        elif self._command_map[key] != urwid.ACTIVATE:
            return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not urwid.util.is_mouse_press(event):
            return False

        return True

    def selectable(self):
        return self._enabled

    def enable(self, enable):
        self._enabled = enable

    def ResetAfterLostFocus(self, reset_after_lost_focus):
        self._reset_after_lost_focus = reset_after_lost_focus

    def EnterFireChangeEvent(self, enter_fire_change_event):
        self._enter_fire_change_event = enter_fire_change_event


### CUSTOM URWID FRAME ###
class CustomFrame(urwid.Frame):

    def keypress(self, size, key):

        if key == 'tab':
            if self.focus_position == 'header' and self.body.selectable():
                self.focus_position = 'body'
            elif self.focus_position == 'header' and self.footer.selectable():
                self.focus_position = 'footer'

            elif self.focus_position == 'body' and self.footer.selectable():
                self.focus_position = 'footer'
            elif self.focus_position == 'body' and self.header.selectable():
                self.focus_position = 'header'

            elif self.focus_position == 'footer' and self.header.selectable():
                self.focus_position = 'header'
            elif self.focus_position == 'footer' and self.body.selectable():
                self.focus_position = 'body'

        urwid.Frame.keypress(self, size, key)


### CUSTOM URWID TEXT ###
class CustomText(urwid.Text):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['resize']

    _size = (0,0)
    _first_render = False
    
    def render (self, size, focus = False):
        canvas = super(CustomText, self).render(size, focus)
        new_size = (canvas.rows(), canvas.cols())
        # check if to raise *on_resize* event
        if new_size != self._size and not self._first_render:
            self._emit('resize', self._size, new_size)
        self._size = new_size
        self._first_render = False
        return canvas

    def get_size(self):
        return self._size


### CUSTOM URWID FILLER ###
class CustomFiller(urwid.Filler):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['resize']

    def __init__(self, body, valign=urwid.MIDDLE, height=urwid.PACK, min_height=None, top=0, bottom=0):
        self._size = (0,0)
        self._first_render = False

        urwid.Filler.__init__(self, body, valign, height, min_height, top, bottom)
    
    def render (self, size, focus = False):
        canvas = super(CustomFiller, self).render(size, focus)
        new_size = (canvas.rows(), canvas.cols())
        # check if to raise *on_resize* event
        if new_size != self._size and not self._first_render:
            self._emit('resize', self._size, new_size)
        self._size = new_size
        self._first_render = False
        return canvas

    def get_size (self):
        return self._size


### TERMINAL UI CLASS ###
class TerminalUI():

    ### INITIALISE ###
    def __init__(self, title, command_entered_callback=None, options=None, option_item_selected_callback=None, options_width_weight=0.3):
        # CONSTANTS
        self.OPTIONS_WIDTH_WEIGHT = options_width_weight

        # VARIABLES
        self._command_entered_callback = command_entered_callback
        self._option_item_selected_callback = option_item_selected_callback

        # UI/WIDGET SETUP
        # Receive Area
        self._InitialiseReceiveArea()

        # Options Area
        if not (options == None or options == {}):
            self._InitialiseOptionsArea(options)
        
        # Body Area - Receive and Options
        if not (options == None or options == {}):
            body = urwid.Columns([('weight', 1-self.OPTIONS_WIDTH_WEIGHT, self.receive_area), ('weight', self.OPTIONS_WIDTH_WEIGHT, self.options_area)])
        else:
            body = self.receive_area

        # Command Area
        self._InitialiseCommandArea()

        # Main Frame
        self.title_text = urwid.Text('%s'%(title), align='center')
        self.main_frame = CustomFrame(body, header=self.title_text, footer=self.command_area)

        if options == None or options == {}:
            self.main_frame.focus_position = 'footer'


    ### RUN ###
    def Run(self):
        main_loop = urwid.MainLoop(self.main_frame, palette=[('reversed', 'standout', '')])
        main_loop.run()
    

    ### COMMAND FUNCTIONS ###
    def _InitialiseCommandArea(self):
        # Setup Command Area Widgets
        self.command_edit = CommandEdit(">>")
        self.command_txt = urwid.Text('Debug')
        self.command_pile = urwid.Pile([self.command_edit, urwid.Divider('-'), self.command_txt])
        self.command_area = urwid.LineBox(self.command_pile)

        # Connect Signals
        urwid.connect_signal(self.command_edit, 'done', self._OnCommandEnter) 

    def _OnCommandEnter(self, widget, command):
        if self._command_entered_callback != None:
            self._command_entered_callback(self, command)

    def SetCommandDebugText(self, text):
        self.command_txt.set_text(text)

    def CommandDebugTextVisible(self, visible):
        if visible:
            self.command_area = urwid.LineBox(self.command_pile)
        else:
            self.command_area = urwid.LineBox(self.command_edit)

        self.main_frame.footer = self.command_area


    ### RECEIVE FUNCTIONS ###
    def _InitialiseReceiveArea(self):
        self.receive_txt = CustomText('')
        self.receive_filler = CustomFiller(self.receive_txt, 'top')
        self.receive_area = urwid.LineBox(self.receive_filler)

    def SetReceiveText(self, text, clear=True):
        if clear or self.receive_txt.get_text()[0].strip() == '':
            self.receive_txt.set_text(text)
        else:
            current_text = self.receive_txt.get_text()[0]
            text_rows = self.receive_txt.get_size()[0] + 1 # plus one for new line about to add
            filler_rows = self.receive_filler.get_size()[0]
            if text_rows >= filler_rows:
                current_text = current_text.split('\n')[text_rows-filler_rows:]
                current_text = "\n".join(current_text)
            current_text = current_text + "\n" + text
            self.receive_txt.set_text(current_text)


    ### OPTIONS FUNCTIONS ###
    def _InitialiseOptionsArea(self, options):
        # Store options dictionary - need to check all names are unique
        self._options = options
        names = []
        for group_key in self._options:
            for option_name in self._options[group_key][0]:
                names.append(option_name)

        if len(names) > len(set(names)):
            raise ReferenceError('All option names must be unique.')
        

        # Generate options body - will also result in _option_widgets list been generated
        self._GenerateOptionsBody()
        
        # Create listbox and options area
        options_listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self._options_body))
        self.options_area = urwid.LineBox(options_listbox) 
    
    def _GenerateOptionsBody(self):
        self._options_body = [urwid.Text('OPTIONS', align='center'), urwid.Divider()]
        self._option_widgets = []

        for group_key in self._options:
            # Options Body - add title if required
            if self._options[group_key][1]:
                self._options_body.append(urwid.Text(group_key, align='center'))

            # Options Body - add buttons
            for option_name in self._options[group_key][0]:
                # Create Button
                button = TextOptionButton(option_name, self._options[group_key][0][option_name])
                urwid.connect_signal(button, 'change', self._OptionItemSelected)
                self._options_body.append(button)
                self._option_widgets.append(button) # also buttons to self.options, used to find buttons

            # Options Body - add divider if required    
            if self._options[group_key][2]:
                self._options_body.append(urwid.Divider()) 

    def _OptionItemSelected(self, widget):
        self.SetReceiveText(str(widget) + str(widget.get_option()[1]), clear=False)

        if self._option_item_selected_callback != None:
            self._option_item_selected_callback(self, widget.get_name(), widget.get_option()[0], widget.get_option()[1])

    def OptionEnable(self, name, enable):
        for widget in self._option_widgets:
            if widget.get_name() == name:
                widget.enable(enable)

    def OptionResetAfterLostFocus(self, name, reset_after_lost_focus):
        for widget in self._option_widgets:
            if widget.get_name() == name:
                widget.ResetAfterLostFocus(reset_after_lost_focus)

    def OptionEnterFireChangeEvent(self, name, enter_for_change):
        for widget in self._option_widgets:
            if widget.get_name() == name:
                widget.EnterFireChangeEvent(enter_for_change)

### USER DEFINED FUNCTIONS ###
def CommandEntered_Testing(terminal_ui : TerminalUI, command):
    
    terminal_ui.SetCommandDebugText(" Debug: %s"%(command))


def OptionItemSelected_Testing(terminal_ui : TerminalUI, name : str, option_index : int, option_string : str):

    if name == 'write_debug':
        if option_string == 'On':
            terminal_ui.CommandDebugTextVisible(True)
        else:
            terminal_ui.CommandDebugTextVisible(False)



### MAIN FUNCTION ###
if __name__ == "__main__":
    # Options
    options = {}
    options['Option Group One'] = ({'option_a': ['A', 'B', 'C'], 'option_b': ['D', 'E'], 'option_c': ['Open']}, True, True)
    options['Option Group Two'] = ({'option_d': ['100', '200']}, True, True)
    options['Option Group Three'] = ({'option_e': ['On', 'Off']}, True, True)
    
    terminal_ui = TerminalUI('Terminal UI v0.1', CommandEntered_Testing, options, OptionItemSelected_Testing)
    terminal_ui.Run()
