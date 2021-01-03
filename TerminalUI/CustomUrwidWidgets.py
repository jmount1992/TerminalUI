#!/usr/bin/env python

### IMPORT MODULES ###
import re
import urwid
from typing import Union

### CUSTOM WIDGETS ###




### CUSTOM URWID EDIT ###
class CommandEdit(urwid.Edit):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['done']

    def __init__(self, caption=u"", edit_text=u"", multiline=False, align=urwid.LEFT, wrap=urwid.SPACE, allow_tab=False, edit_pos=None, layout=None, mask=None, history_size=50, enable=True):

        self._history = []
        self._history_idx = -1
        self._history_size = history_size
        self._enabled = enable

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

    def selectable(self):
        return self._enabled

    def enable(self, enable):
        self._enabled = enable

### CUSTOM OPTION ###
class UserOption(urwid.WidgetWrap):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['value_change']

    def __init__(self, option_name : str, value : Union[list, str, int, float], caption : str="", increment : Union[int, float]=None, limits : Union[int, float, list]=[None, None], enter_fires_change_event : bool=True, enabled : bool=True):
        # Variables
        self._option_name = option_name
        self._value_list = None             # holds the list of selectable values, if passed values is a list, else will be none
        self._current_value = 0             # holds the current value, or current index of selected _values_list, if value is a list of selectable options
        self._shown_value = 0               # holds the current value shown to the user
        self._caption = caption
        self._increment = increment
        self._limits = limits               # limits that self._current_value and self._shown value can take, inclusive
        self._enter_fires_change_event = enter_fires_change_event
        self._enabled = enabled
        self._editing = False


        # Set self._value_list, self._current_value and self._shown_value
        if type(value) == list:
            # value contains a list of selectable options
            self._value_list = value
            self._current_value = 0
            self._shown_value = 0
            self._increment = 1                         # to increment list value by 1
            self._limits = [0, len(self._value_list)-1]   # limits are 0 and length of list

            # Initialise urwid selectable icon to contain user option value
            self._option_text = urwid.SelectableIcon("???")
            self._option_text.set_align_mode("center")
            self._set_option_text(self._current_value)
            self._set_option_text_curs_pos()

        else:
            self._current_value = value
            self._shown_value = value

            if type(value) == str:
                self._increment = None # incrementing a string does not make sense

            # Initialise urwid edit text to contain user option value
            self._option_text = urwid.Edit(edit_text="???", align='center', edit_pos=None)
            self._set_option_text(self._current_value)
            self._set_option_text_curs_pos()

        # Initialise remaining urwid widgets
        if caption.strip() != "":
            self._caption_text = urwid.Text(caption, align='center')
            option = urwid.Columns([self._caption_text, self._option_text])
        else:
            option = self._option_text
        option = urwid.AttrMap(option, None, focus_map='reversed')
        self.__super.__init__(option)


    def _set_option_text(self, value):
        if type(self._option_text) == urwid.SelectableIcon:
            txt = "< %s >"%(str(self._value_list[value]))
            self._option_text.set_text(txt)
        elif type(self._option_text) == urwid.Edit:
            if self._increment != None:
                txt = "< %s >"%(str(value))
            else:
                txt = "%s"%(str(value))
            self._option_text.set_edit_text(txt)

    def _set_option_text_curs_pos(self):
        if type(self._option_text) == urwid.SelectableIcon:
            tmp_list = [str(x) for x in self._value_list]
            curs_pos = len(max(tmp_list, key=len)) + 5 # to hide the cursor so don't see it flashing, +4 for < and > and two spaces then +1 to put at end
            self._option_text._cursor_position = curs_pos
        elif type(self._option_text) == urwid.Edit:
            # doesn't seem to work at the moment
            curs_pos = len(self._option_text.get_edit_text()) - 2 # to move cursor to last place, doesn't seem to be working
            self._option_text.edit_pos = curs_pos

    
    def sizing(self):
        return frozenset([urwid.FLOW])

    def set_option_name(self, option_name : str):
        self._option_name = option_name

    def get_option_name(self):
        return self._option_name

    def set_caption(self, caption : str):
        self._caption = caption
        self._caption_text.set_text(caption)

    def get_caption(self):
        return self._caption

    def set_value(self, value : Union[str, int, float]):
        if type(self._option_text) == urwid.SelectableIcon:
            if type(value) == int or type(value) == float:
                if type(value) == float and not value.is_integer():
                    raise RuntimeError('The passed list option index be an integer not a float.')
                if value < 0 or value > self._limits[1]:
                    raise RuntimeError('The passed list option index is outside the selectable option value list range.')
                self._current_value = int(value)
            elif type(value) == str:
                if value in self._value_list:
                    self._current_value = self._value_list.index(value)

        elif type(self._option_text) == urwid.Edit:            
            if self._limits[0] != None:
                value = max(value, self._limits[0])
            if self._limits[1] != None:
                value = min(value, self._limits[1])
            self._current_value = value

        # set option text
        self._shown_value = self._current_value
        self._set_option_text(self._current_value)

    def get_value(self):
        if type(self._option_text) == urwid.SelectableIcon:
            retval = self._value_list[self._current_value]
        elif type(self._option_text) == urwid.Edit:
            retval = self._current_value

        # if it isn't a string return whatever value is
        if type(retval) != str:
            return retval

        # attempt to convert from str to float, int or bool
        if re.match('^[0-9\.]*$', retval): # float
            return float(retval)
        elif re.match('^[0-9]*$', retval): # integer
            return int(retval)
        elif retval.lower() == 'true': # true
            return True
        elif retval.lower() == 'false': # false
            return False

        return retval # just return the value as is


    def get_value_index(self):
        if type(self._option_text) == urwid.SelectableIcon:
            return self._current_value
        elif type(self._option_text) == urwid.Edit:
            return None

    def set_option_list(self, values_list : list, index : int=0):
        if type(self._option_text) == urwid.SelectableIcon:
            self._value_list = values_list
            self._limits = [0, len(self._value_list)-1]   # limits are 0 and length of list
            self.set_value(index)
            self._set_option_text(self._current_value)
            self._set_option_text_curs_pos()
            
            return True
        else:
            return False

    def get_option_list(self):
        return self._value_list

    def selectable(self):
        return self._enabled

    def enable(self, enable):
        self._enabled = enable

    def valid_numerical_char(self, ch):
        """
        Return true for decimal digits.
        """
        return len(ch)==1 and ch in "0123456789.-"

    def valid_char(self, ch):
        """
        Filter for text that may be entered into this widget by the user

        :param ch: character to be inserted
        :type ch: bytes or unicode

        This implementation returns True for all printable characters.
        """
        return urwid.util.is_wide_char(ch,0) or (len(ch)==1 and ord(ch) >= 32)

    def mouse_event(self, size, event, button, x, y, focus):
        pass 
        # if button != 1 or not urwid.util.is_mouse_press(event):
        #     return False

        # return True
        

    def keypress(self, size, key):
        # Handle left/right arrow keypresses
        if self._command_map[key] == urwid.CURSOR_LEFT or self._command_map[key] == urwid.CURSOR_RIGHT:
            return self._handle_left_right_keypresses(size, key)

        # Handle up/down arrow keypresses
        elif self._command_map[key] == urwid.CURSOR_UP or self._command_map[key] == urwid.CURSOR_DOWN:
            return self._handle_up_down_keypresses(size, key)

        # Handle enter keypress
        elif key == 'enter':
            return self._handle_enter_keypress(size, key)

        # Handle escape keypress
        elif key == 'esc':
            self._editing = False
            self.set_value(self._current_value)
            return # nothing to show keypress has been handled

        # Handle printable character keypress or backspace or delete
        if self.valid_char(key) or key == 'backspace' or key == 'delete':
            return self._handle_edit_keypress(size, key)
        
        # So higher widgets can deal with keypress
        return key


    def _handle_left_right_keypresses(self, size, key):
        # If not currently being edited and increment is not none, increment/decrement value
        if self._editing == False and self._increment != None:
            if self._command_map[key] == urwid.CURSOR_LEFT:
                self._decrement_value()
            else:
                self._increment_value()

            # show new value
            self._set_option_text(self._shown_value)

            # fire change event if self._enter_fires_change_event is false, and only fire change event if current and shown is different
            if self._enter_fires_change_event == False and (self._current_value != self._shown_value):
                self.set_value(self._shown_value)
                self._emit('value_change')

        elif self._editing or self._increment == None:
            p = self._option_text.edit_pos

            if self._command_map[key] == urwid.CURSOR_LEFT:
                if p == 0: 
                    return key
                p = urwid.util.move_prev_char(self._option_text.get_edit_text(), 0, p)
                self._option_text.set_edit_pos(p)

            elif self._command_map[key] == urwid.CURSOR_RIGHT:
                if p >= len(self._option_text.get_edit_text()): 
                    return key
                p = urwid.util.move_next_char(self._option_text.get_edit_text(), p, len(self._option_text.get_edit_text()))
                self._option_text.set_edit_pos(p)

    def _handle_up_down_keypresses(self, size, key):
        self._editing = False

        if self._shown_value != self._current_value:
            if self._enter_fires_change_event:
                # enter cause event change, reset to current value as enter was not pressed
                self.set_value(self._current_value)
            else:
                self.set_value(self._shown_value)
                self._emit('value_change')
        
        return key

    def _handle_enter_keypress(self, size, key):
        if (self._enter_fires_change_event or self._editing): # and self._current_value != self._shown_value
            self._editing = False
            self.set_value(self._shown_value)
            self._emit('value_change')

    def _handle_edit_keypress(self, size, key):
        # If valid printable character, or backspace or delete and increment is none, assume editing a string
        if (self.valid_char(key) or key == 'backspace' or key == 'delete') and self._increment == None:
            # handle key
            self._editing = True
            urwid.Edit.keypress(self._option_text, size, key)
            self._shown_value = self._option_text.get_edit_text()

        # Else if valid numerical character, or backspace or delete and increment is not none, assume editing a number
        elif (self.valid_numerical_char(key) or key == 'backspace' or key == 'delete') and self._increment != None:
            # handle key
            self._editing = True
            current_text = self._option_text.get_edit_text()
            urwid.Edit.keypress(self._option_text, size, key)
            tmp_txt = self._option_text.get_edit_text()

            # don't allow editing of starting '< ' and ending ' >' substrings
            if self._increment != None and (tmp_txt[0:2] != '< ' or tmp_txt[-2:] != ' >'):
                self._option_text.set_edit_text(current_text)
                return
            
            if self._increment != None:
                tmp_txt = tmp_txt[2:-2] # ignore starting and ending substrings
            
            if not (tmp_txt.strip() == '.' or tmp_txt.strip() == '-' or tmp_txt.strip() == ''):
                try:
                    tmp_val = float(tmp_txt) 
                    self._shown_value = tmp_val
                except ValueError:
                    # reset back to shown value
                    self._option_text.set_edit_text(current_text)
            else:
                self._shown_value = 0
                self._option_text.set_edit_text('< 0 >')

    def _increment_value(self):
        self._shown_value += self._increment
        if self._limits[1] != None and self._shown_value > self._limits[1]:
            if type(self._option_text) == urwid.SelectableIcon:
                self._shown_value = self._limits[0]     # wrap value
            elif type(self._option_text) == urwid.Edit:
                self._shown_value = self._limits[1]     # do not wrap value

    def _decrement_value(self):
        self._shown_value -= self._increment
        if self._limits[0] != None and self._shown_value < self._limits[0]:
            if type(self._option_text) == urwid.SelectableIcon:
                self._shown_value = self._limits[1]     # wrap value
            elif type(self._option_text) == urwid.Edit:
                self._shown_value = self._limits[0]     # do not wrap value


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