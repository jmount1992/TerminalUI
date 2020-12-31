#!/usr/bin/env python

# ### IMPORT MODULES ###
import urwid
from typing import Callable, Union
from TerminalUI.CustomUrwidWidgets import *


### TERMINAL UI CLASS ###
class TerminalUI():
    """The TerminalUI class is used to create a terminal user interface that can be used for asynchronous read/write operations (e.g. Serial Communications) with an optional options menu for changing application code. All that is required is a user-defined function to be called when a write command is entered, and if desired an options menu and a user-defined function to be called when an option value is changed.

    Raises:
        RuntimeError: on construction, if the options is not a dictionary
        RuntimeError: on construction, if the value for each key in options is not a dictionary or a tuple
        RuntimeError: on construction, if the length of the tuple for the group name key value has a length greater than 3
        RuntimeError: on construction, if all options names are not unique
        RuntimeError: on construction, if it is a selectable option list passed as part of a tuple and the tuple has a length greater than 4
        RuntimeError: on construction, if it is an editable value option passed as part of a tuple and the tuple has a length greater than 6
        RuntimeError: on construction, if the value for the option name key is not a str, int, float, list or tuple
    """

    ### INITIALISE ###
    def __init__(self, title : str, command_entered_callback : Callable[['TerminalUI', str], None], options : dict=None, option_item_selected_callback : Callable[['TerminalUI', str, Union[int, float, bool, str], int], None]=None, options_width_weight : float=0.3):
        """The constructor for the TerminalUI class, will initiliase variables and screen widgets. 
        See https://github.com/jmount1992/TerminalUI/tree/main/examples/option_example.py for details and a code example on setting the options argument

        Args:
            title (str): The title wishing to place at the top of the TerminalUI screen
            command_entered_callback (Callable[[TerminalUI, str], None]): The function to run when a command is entered by the user
            options (dict, optional): A dictionary containing options and their values as well as display information. Defaults to None. 
            option_item_selected_callback (Callable[[TerminalUI, str, Union[int, float, bool, str], int], None], optional): The function to run when an option change event fires. Defaults to None. 
            options_width_weight (float, optional): The amount of the screen width to use for the options area, rest will be used for receive textbox. Defaults to 0.3.

        Raises:
            RuntimeError: if the options is not a dictionary
            RuntimeError: if the value for each key in options is not a dictionary or a tuple
            RuntimeError: if the length of the tuple for the group name key value has a length greater than 3
            RuntimeError: if all options names are not unique
            RuntimeError: if it is a selectable option list passed as part of a tuple and the tuple has a length greater than 4
            RuntimeError: if it is an editable value option passed as part of a tuple and the tuple has a length greater than 6
            RuntimeError: if the value for the option name key is not a str, int, float, list or tuple
        """


        # CONSTANTS
        self.OPTIONS_WIDTH_WEIGHT = options_width_weight

        # VARIABLES
        self._command_entered_callback = command_entered_callback
        self._option_item_selected_callback = option_item_selected_callback
        self._command_debug_visible = True

        # UI/WIDGET SETUP
        # Receive Area
        self._initialise_receive_area()

        # Options Area
        if not (options == None or options == {}):
            self._initialise_options_area(options)
        
        # Body Area - Receive and Options
        if not (options == None or options == {}):
            body = urwid.Columns([('weight', 1-self.OPTIONS_WIDTH_WEIGHT, self.receive_area), ('weight', self.OPTIONS_WIDTH_WEIGHT, self.options_area)])
        else:
            body = self.receive_area

        # Command Area
        self._initialise_command_area()

        # Main Frame
        self.title_text = urwid.Text('%s'%(title), align='center')
        self.main_frame = CustomFrame(body, header=self.title_text, footer=self.command_area)

        if options == None or options == {}:
            self.main_frame.focus_position = 'footer'


    ### RUN ###
    def run(self, redraw_period=0.1):
        """Will start running the TerminalUI, drawing widgets to screen and capturing events.

        Args:
            redraw_period (float, optional): Will redraw the screen every X seconds. Used to update widgets when they are updated from a separate thread. If set to 0, no update will occur. Defaults to 0.1.
        """

        self.main_loop = urwid.MainLoop(self.main_frame, palette=[('reversed', 'standout', '')])
        if redraw_period != 0:
            self.main_loop.set_alarm_in(redraw_period, self._redraw, user_data=redraw_period)
            self.main_loop.run()

    def exit(self):
        """Exits the urwid event loop. Use this to close the TerminalUI after calling TerminalUI.run().
        """
        raise urwid.ExitMainLoop
    
    def _redraw(self, main_loop, redraw_period=0.1):
        """Redraws the screen and set an alarm to redraw in X seconds.

        Args:
            main_loop ([type]): the urwid MainLoop object
            redraw_period (float, optional): The number of seconds until redraw the screen again. Set to 0 to not redraw. Defaults to 0.1.
        """
        main_loop.draw_screen()
        if redraw_period != 0:
            main_loop.set_alarm_in(redraw_period, self._redraw, redraw_period)

    ### COMMAND FUNCTIONS ###
    def _initialise_command_area(self):
        """Initiliases the command area which contains Edit and Text widgets."""

        # Setup Command Area Widgets
        self.command_edit = CommandEdit(">>")
        self.command_txt = urwid.Text('Debug')
        self.command_area = self._get_command_area()

        # Connect Signals
        urwid.connect_signal(self.command_edit, 'done', self._on_command_enter) 

    def _on_command_enter(self, widget : urwid.Widget, command : str):
        """Event handler that calls the used defined command_entered_callback function passed to the constructor.

        Args:
            widget (urwid.Widget): the widget that signalled the event.
            command (str): the string entered into the edit widget
        """

        self._command_entered_callback(self, command)

    def _get_command_area(self) -> urwid.Widget:
        """Builds and returns the complete widget for the command area.

        Returns:
            urwid.Widget: returns the widget for the command area
        """
        command_pile = urwid.Pile([self.command_edit, urwid.Divider('-'), self.command_txt])
        if self._command_debug_visible:
            command_area = urwid.LineBox(command_pile)
        else:
            command_area = urwid.LineBox(self.command_edit)
        
        return command_area

    def set_command_debug_text(self, text, clear : bool=True):
        """Sets the text within the command debug textbox.
        
        Args:
            clear (bool, optional): used to specify if wish to clear current text within the textbox. Defaults to True.
        """
        if clear or self.command_txt.get_text()[0].strip() == '':
            self.command_txt.set_text(text)
        else:
            current_txt = self.command_txt.get_text()[0]
            self.command_txt.set_text(current_txt + text)

    def command_debug_text_visible(self, visible):
        """Used to show/hide the command debug textbox."""

        self._command_debug_visible = visible
        self.main_frame.footer = self._get_command_area()

    def enable_command(self, enable : bool):
        """Used to enable/disable the command edit text area.

        Args:
            enable (bool): used to specify if the write command edit text is selectable
        """

        self.command_edit.enable(enable)
        self.main_frame.footer = self._get_command_area()


    ### RECEIVE FUNCTIONS ###
    def _initialise_receive_area(self):
        """Initiliases the receive area textbox and filler widgets."""

        self.receive_txt = CustomText('')
        self.receive_filler = CustomFiller(self.receive_txt, 'top')
        self.receive_area = urwid.LineBox(self.receive_filler)

    def set_receive_text(self, text : str, clear : bool=True):
        """Sets the text within the receive textbox.

        Args:
            text (str): the string for the receive textbox
            clear (bool, optional): used to specify if wish to clear current text within the textbox. Defaults to True.
        """

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
    def _initialise_options_area(self, options : dict):
        """Initiliases the options area widgets and checks options data is valid.

        Args:
            options (dict): the options data dictionary passed to the TerminalUI constructor.

        Raises:
            RuntimeError: if the options is not a dictionary
            RuntimeError: if the value for each key in options is not a dictionary or a tuple
            RuntimeError: if the length of the tuple for the group name key value has a length greater than 3
            RuntimeError: if all options names are not unique
        """     

        # Make sure options is a dictionary
        if type(options) != dict:
            raise RuntimeError('The passed options must be a dictionary')

        # Store options dictionary - need to check all names are unique
        self._options = options
        names = []
        for group_key in self._options:
            # Get data from group name - this is dependent on type
            if type(self._options[group_key]) == dict:
                group_options_dict = self._options[group_key]
            elif type(self._options[group_key]) == tuple:
                # First element in tuple will be a dictionary containing the option names dictionary
                group_options_dict = self._options[group_key][0]
                if len(self._options[group_key]) > 3:
                    raise RuntimeError('The length of the tuple for the value field for the %s key must have a length no greater than 3'%(group_key))
            else:
                raise RuntimeError('The value of the %s key within options should be dictionary or a tuple.'%(group_key))

            # Get keys from group_options_dict
            for option_name in group_options_dict:
                names.append(option_name)

        if len(names) > len(set(names)):
            raise RuntimeError('All option names must be unique.')
        
        # Generate options body - will also result in _option_widgets list been generated
        self._generate_options_body()
        
        # Create listbox and options area
        options_listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self._options_body))
        self.options_area = urwid.LineBox(options_listbox) 
    
    def _generate_options_body(self):
        """Generates the list of widgets for the options area.

        Raises:
            RuntimeError: if it is a selectable option list passed as part of a tuple and the tuple has a length greater than 4
            RuntimeError: if it is an editable value option passed as part of a tuple and the tuple has a length greater than 6
            RuntimeError: if the value for the option name key is not a str, int, float, list or tuple
        """

        self._options_body = [urwid.Text('OPTIONS', align='center'), urwid.Divider()]
        self._option_widgets = []

        for group_key in self._options:
            # Get data from group key
            if type(self._options[group_key]) == dict:
                group_options_data = self._options[group_key]
                show_title = True
                divider_on = True
            elif type(self._options[group_key]) == tuple:
                # First element in tuple will be a dictionary containing the option names dictionary
                group_options_data = self._options[group_key][0]
                if len(self._options[group_key]) == 2:
                    # Assume second element is show title
                    show_title = self._options[group_key][1]
                elif len(self._options[group_key]) == 3:
                    # Assume second element is show title and divider on is third element
                    show_title = self._options[group_key][1]
                    divider_on = self._options[group_key][2] 

            # Add urwid.Text() widget to _options_body to be used as a title if required
            if show_title:
                self._options_body.append(urwid.Text(group_key, align='center'))

            # Add buttons to _options_body 
            for option_name in group_options_data:

                # Create defaults for optional components
                caption = ""
                increment = None
                limits = [None, None]
                enter_fires_change_event = True
                enabled = True

                # Create a UserOption widget
                option_data = group_options_data[option_name]

                # Determine if option_data is a list, a single value or a tuple containing optional UserOption parameters
                if type(option_data) == tuple:
                    # Option data contains optional UserOption parameters

                    # Get value component from option_data tuple
                    value = option_data[0]
                    
                    # Value component will determine if is a list of selectable values or an editable value
                    if type(value) == list:
                        # list of selectable values
                        if len(option_data) == 2:
                            caption = option_data[1]
                        elif len(option_data) == 3:
                            caption = option_data[1]
                            enter_fires_change_event = option_data[2]
                        elif len(option_data) == 4:
                            caption = option_data[1]
                            enter_fires_change_event = option_data[2]
                            enabled = option_data[3]
                        else:
                            raise RuntimeError('The tuple containing the option data when the option is a list of selectable values must have a length less of 4 or less.')
                    elif type(value) == int or type(value) == float or type(value) == str:
                        # editable value
                        if len(option_data) == 2:
                            caption = option_data[1]
                        elif len(option_data) == 3:
                            caption = option_data[1]
                            increment = option_data[2]
                        elif len(option_data) == 4:
                            caption = option_data[1]
                            increment = option_data[2]
                            limits = option_data[3]
                        elif len(option_data) == 5:
                            caption = option_data[1]
                            increment = option_data[2]
                            limits = option_data[3]
                            enter_fires_change_event = option_data[4]
                        elif len(option_data) == 6:
                            caption = option_data[1]
                            increment = option_data[2]
                            limits = option_data[3]
                            enter_fires_change_event = option_data[4]
                            enabled = option_data[5]
                        else:
                            raise RuntimeError('The tuple containing the option data when the option is an editable value must have a length less of 6 or less.')

                    
                elif type(option_data) == list:
                    # option_data is a list of selectable values
                    value = option_data

                elif type(option_data) == int or type(option_data) == float or type(option_data) == str:
                    # option_data is an editable value
                    value = option_data

                else:
                    raise RuntimeError('The option data must be a list, int, float or str, or a tuple where the first element is a list, int, float or str')

                # print(option_name, value, caption, increment, limits, enter_fires_change_event, enabled)

                # Create the actual widget, connect the change signal, append user_option to body and option_widgets list
                user_option = UserOption(option_name, value, caption, increment, limits, enter_fires_change_event, enabled)
                urwid.connect_signal(user_option, 'value_change', self._option_item_selected)
                self._options_body.append(user_option)
                self._option_widgets.append(user_option) # used to find user_options

            # Add urwid.Divider() widget to _options_body if required
            if divider_on:
                self._options_body.append(urwid.Divider()) 

    def _option_item_selected(self, widget : urwid.Widget):
        """Event handler that calls the used defined option_item_selected_callback function passed to the constructor.

        Args:
            widget (urwid.Widget): The widget that raised the change event
        """

        if self._option_item_selected_callback != None:
            self._option_item_selected_callback(self, widget.get_option_name(), widget.get_value(), widget.get_value_index())
        


    def set_option(self, option_name : str, option_value : Union[int, str, float]) -> bool:
        """Used to set an option given an option_name and either a string or integer representing the desired option value. The option string or integer must exist else no change will occur."

        Args:
            option_name (str): The name of the option wish to set
            option_value (Union[str, int]): The string or integer index value for the desired option value

        Returns:
            bool: true if the option was changed, false if no option exists with the passed option_name or if the option string or integer index value for that option does not exist
        """
        
        # Find widget with that name
        widget = None
        for tmp_widget in self._option_widgets:
            if tmp_widget.get_option_name() == option_name:
                widget = tmp_widget
                break
        
        if widget is None:
            return False

        # Try to set option
        try:
            widget.set_value(option_value)
            return True
        except RuntimeError:
            return False


    def get_option(self, option_name : str):
        """Gets the value and index, if the option is a list of selectable values, for the specified option name. The return type for the value will automatically be converted to a int, float or bool if possible, else it will be returned as a string.

        Args:
            option_name (str): the name of the option want the value for

        Returns:
            tuple: (successful, value, index). Successfull will be true if an option with the given name could be found. The value will contain the value of the option. The index will contain the list index if the option is a list of selectable values.
        """

        for widget in self._option_widgets:
            if widget.get_option_name() == option_name:
                return True, widget.get_value(), widget.get_value_index()

        return False, None, None

    def set_option_list(self, option_name : str, options : list, idx : int=0) -> bool:
        """Sets the option list for selectable list option. Will do nothing if the option is an editable value.

        Args:
            option_name (str): the name of the option to set the list for
            options (list): the list of selectable values
            idx (int, optional): the index of the list to display. Defaults to 0.

        Returns:
            bool: if the list was successfull set
        """
        # Find widget with that name
        widget = None
        for widget in self._option_widgets:
            if widget.get_option_name() == option_name:
                return widget.set_option_list(options, idx)
        
        return False

    def enable_option(self, option_name : str, enable : bool):
        """Enables/Disables an option

        Args:
            name (str): The name of the option want to enable/disable
            enable (bool): Specify to true/false if wanting to enable/disable the option
        """

        for widget in self._option_widgets:
            if widget.get_option_name() == option_name:
                widget.enable(enable)

    def option_enter_fires_change_event(self, option_name : str, enter_fires_change_event : bool):
        """Speficies if an option fires a change event when the enter or space key is pressed or if the change event is fired as soon as the option is changed (i.e. left/arrow key alters option).

        Args:
            name (str): The name of the option want to change when event fires
            enable (bool): Specify to true if want to fire change event when enter or space is pressed, or false as soon as option text is changed.
        """

        for widget in self._option_widgets:
            if widget.get_option_name() == option_name:
                widget.enter_fires_change_event(enter_fires_change_event)


    ### TIMER EVENTS ###
    def set_alarm_in(self, sec : float, callback : callable, user_data=None):
        """Set an alarm to fire an event in x seconds and to run a specific function with the passed user data.

        Args:
            sec (float): The number of seconds to wait before firing the event
            callback (callable): The function to call when the event fires
            user_data (optional): Any specified user data. Defaults to None.
        """
        self.main_loop.set_alarm_in(sec, callback, user_data)






