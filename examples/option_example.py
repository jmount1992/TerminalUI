#!/usr/bin/env python3

### IMPORT MODULES ###
from typing import Union
from TerminalUI import TerminalUI


### USER DEFINED FUNCTIONS ###
def command_entered_testing(terminal_ui : TerminalUI, command : str):
    """An example function that could be passed into the TerminalUI command_entered_callback argument, which will be called everytime a user enters a command.

    Args:
        terminal_ui (TerminalUI): The TerminalUI object that called the command_entered_callback function
        command (str): The command entered by the user
    """
    
    # Set the command debug textbox to contain the command entered by the user
    terminal_ui.set_command_debug_text(" Debug: %s"%(command))


def option_item_selected_testing(terminal_ui : TerminalUI, option_name : str, value : Union[int, float, bool, str], index : int):
    """An example function that could be passed into the TerminalUI option_item_selected_callback argument, which will be called everytime an option fires its change event.
    
    Args:
        terminal_ui (TerminalUI): The TerminalUI object that called the option_item_selected_callback function
        option_name (str): The name of the option that fired the change event
        value (Union[int, float, bool, str]): The value of the option
        index (int): The index of the value if the option is a list of selectable values
    """

    # Add text specifying the option_name and the option_string to the receive textbox
    txt = 'Option Name: %s, Current Value: %s, Index: %s'%(option_name, value, str(index))
    terminal_ui.set_receive_text(txt, clear=False)

    # If the enable_options option fired the change event
    if option_name == 'enable_options':
        terminal_ui.enable_option('option_3', value)
        terminal_ui.enable_option('option_4', value)
        terminal_ui.enable_option('option_10', value)
        terminal_ui.enable_option('option_11', value)

    # if the enable_command option fired the change event
    elif option_name == 'enable_command':
        terminal_ui.enable_command(value)

    # if the show_cmd_debug option is fired
    elif option_name == 'show_cmd_debug':
        terminal_ui.command_debug_text_visible(value)



### MAIN FUNCTION ###
if __name__ == "__main__":    
    # Create a dictionary with the group names for the user options that will form each set.
    # the key is the group name and will be used as title if desired
    # the value is secondary dictionary containing the option data
    options = {'Selectable List Options': {}, 'Editable Value Options': {}, 'Enable Items': {}}#, 'Demo Group 1': {}, 'Demo Group 2': {}}

    # Create secondary dictionary for the Selectable List Options group. 
    # Selectable list option data must either be a list of selectable options, 
    # or a tuple where the first element is a list of selectable list options 
    # and the remaining elements are optional parameters. Tuple arguments are 
    # (list_of_values, caption, enter_fires_change_event, enable)
    selectable_list_option_data = {}

    # Add in a list of selectable string values for option 1
    selectable_list_option_data['option_1'] = ['A', 'B', 'C']

    # Add in a list of selectable integer values for option 2, with the caption 'Option 2', 
    # fire the change event as soon as the value changes and enable the option
    selectable_list_option_data['option_2'] = ([1, 2, 3], 'Option 2', False, True)

    # Add in a list of selectable floats, with the caption 'Option 3', fire the change event 
    # only when enter is pressed and enable the option
    selectable_list_option_data['option_3'] = ([0.5, 1, 2], 'Option 3', True, False)

    # Add in a list of boolean, with caption 'Option 4', fire the change event as soon as the
    # value changes and disable the option
    selectable_list_option_data['option_4'] = ([True, False], 'Option 4', False, False)

    # Create a secondary dictionary for the Editable Value Options group.
    # An editable value option must either be a single value (i.e. not a list),
    # or a tuple where the first element is a single value and the remaining 
    # elements are optional parameters. The tuple arguments are
    # (value, caption, increment, [min_limit, max_limit], enter_fires_change_event, enable)
    # Note that if the value is a string, then increment will be automatically set to None
    # Even if enter_fires_change_event is set to False, if the value is edited via the keyboard
    # enter must be pressed to fire the change event
    editable_value_option_data = {}

    # Add in an editable value option with an initial value of 1. As no increment argument is provided
    # the increment value will take on the value of None and hence this option can be edited to contain
    # any printable character (i.e. it could become a string rather than a number). If you wish to force
    # it to stay a number see option 6
    editable_value_option_data['option_5'] = 1

    # Add in an editable value option with an initial value of 1. As increment value is set to 0, this
    # editable value can only take on numbers
    editable_value_option_data['option_6'] = (1, '', 0)

    # Add in an editable value with an initial value of 'Editable String' with the caption 'Option 7'.
    # As initial value is a string, increment will be set to None, no matter what argument is passed.
    editable_value_option_data['option_7'] = ('Editable String', 'Option 7')

    # Add in editable value with an initial value of 0.5 with the caption of 'Option 8' and set the
    # increment value to 1
    editable_value_option_data['option_8'] = (0.5, 'Option 8', 1)

    # Add in editable value with an initial value of 0 with the caption of 'Option 9' and set the
    # increment value to 0.5 with limits of -5 and 5.
    editable_value_option_data['option_9'] = (0, 'Option 9', 0.5, [-5, 5])

    # Add in editable value with an initial value of 0 with the caption of 'Option 10' and set the
    # increment value to 0.5 with limits of -5 and 5. Fire change event as soon as value is changed
    # and enable the option
    editable_value_option_data['option_10'] = (0, 'Option 10', 0.5, [-5, 5], False, True)

    # Add in editable value with an initial value of 0 with the caption of 'Option 11' and set the
    # increment value to 0.5 with limits of -5 and 5. Fire change event only when enter is pressed
    # and disable the option
    editable_value_option_data['option_11'] = (0, 'Option 11', 0.5, [-5, 5], True, False)

    # Add in editable value with an initial value of 0 with the caption of 'Option 12' and set the
    # increment value to 0.5 with limits of -5 and 5. Fire change event as soon as value is changed
    # and disable the option
    editable_value_option_data['option_12'] = (0, 'Option 12', 0.5, [-5, 5], False, False)

    # Create a secondary dictionary for the Enable Items group. This consists of three selectable list
    # options and is used to show how one can disable/enable buttons and other aspects of the TerminalUI
    # class
    enable_group_option_data = {}
    enable_group_option_data['enable_options'] = ([True, False], 'Enable All Options')
    enable_group_option_data['enable_command'] = ([True, False], 'Enable Commands')
    enable_group_option_data['show_cmd_debug'] = ([True, False], 'Show Command Debug', False)

    # Create a secondary dictionary for the Demo Group 1. You can combine both selectable list options
    # and editable value options in a single group.
    demo_group_1_option_data = {}
    demo_group_1_option_data['option_13'] = (['A', 'B', 'C'], 'Caption')
    demo_group_1_option_data['option_14'] = ('Editable String', 'Caption')

    # Create a secondary dictionary for the Demo Group 2. Selectable lists do not need to
    # contain values of the same type
    demo_group_2_option_data = {}
    demo_group_2_option_data['option_15'] = (['ABC', 1, 0.5], 'Caption')


    # Set the secondary dictionary of each group
    options['Selectable List Options'] = selectable_list_option_data
    options['Editable Value Options'] = editable_value_option_data
    options['Enable Items'] = enable_group_option_data

    # Each group has two optional parameters which can be passed via a tuple. 
    # The first element must be the secondary dictionary containing the option data.
    # The second and third element are booleans which can be used to specify if the
    # group name is shown above the option set as a title and if a blank row is left 
    # after the option set respectively.
    # options['Demo Group 1'] = (demo_group_1_option_data, True, True) # show the title and have a blank row after the set
    # options['Demo Group 2'] = (demo_group_2_option_data, False, False) # hide the title and do not have a blank row after the set


    # Create TerminalUI object with the title 'Terminal UI v0.1', command_entered_testing function callback, 
    # the options specified and the option_item_selected_testing callback function.
    terminal_ui = TerminalUI('Terminal UI v0.1', command_entered_testing, options, option_item_selected_testing)

    # Set initial value for the enable_options command to be disabled
    terminal_ui.set_option('enable_options', 1)

    # Run the terminal UI
    terminal_ui.run()