#!/usr/bin/env python3

### IMPORT MODULES ###
import time
import threading
from typing import Union
from TerminalUI import TerminalUI


### USER DEFINED FUNCTIONS ###
def command_entered_testing(terminal_ui : TerminalUI, command : str):
    """An example function that could be passed into the TerminalUI command_entered_callback argument, which will be called everytime a user enters a command.

    Args:
        terminal_ui (TerminalUI): The TerminalUI object that called the command_entered_callback function
        command (str): The command entered by the user
    """
    
    # Convert command string into a byte array
    byte_array = bytearray([ord(x) for x in command])
    byte_array_hex_string = ("".join(" 0x%02x"%(x) for x in byte_array)).strip()

    # Set the command debug textbox to contain the command entered by the user as plain text and as a hex coded byte array
    txt = " Input Text: %s"%command
    txt += "\n HEX Bytes Sent: %s"%byte_array_hex_string
    terminal_ui.set_command_debug_text(txt)


def option_item_selected_testing(terminal_ui : TerminalUI, option_name : str, value : Union[int, float, bool, str], index : int):
    """An example function that could be passed into the TerminalUI option_item_selected_callback argument, which will be called everytime an option fires its change event.
    
    Args:
        terminal_ui (TerminalUI): The TerminalUI object that called the option_item_selected_callback function
        option_name (str): The name of the option that fired the change event
        value (Union[int, float, bool, str]): The value of the option
        index (int): The index of the value if the option is a list of selectable values
    """
    global enable_read

    # enable/disable enable_read
    if option_name == 'read_enabled':
        enable_read = value
        terminal_ui.set_receive_text('Read Enabled: %s'%str(value), False)

def read_thread_callback():
    global threads_enabled, enable_read

    while threads_enabled:

        while threads_enabled and enable_read:
            
            # Create text to dump into receive textbo
            txt = time.strftime("%Y-%m-%d %H:%M:%S - Read", time.gmtime(time.time()))
            terminal_ui.set_receive_text(txt, False)
            
            # sleep for 1 second
            time.sleep(1)

### MAIN FUNCTION ###
threads_enabled = True
enable_read = True
read_thread = None

if __name__ == "__main__":    
    # Options
    options = {'Read Settings': {'read_enabled': ([True, False], 'Read Enabled', False)}}

    # Create TerminalUI object with the title 'Terminal UI v0.1', command_entered_testing function callback, 
    # the options specified and the option_item_selected_testing callback function.
    terminal_ui = TerminalUI('Terminal UI v0.1', command_entered_testing, options, option_item_selected_testing)


    # Start serial read thread
    read_thread = threading.Thread(target=read_thread_callback, args=())
    read_thread.start()

    # Run the terminal catching crtl+c keyboard interrupt to close everything appropriately
    try:
        terminal_ui.run()
    except KeyboardInterrupt:
        pass

    # Close appropriately
    enable_read = False
    threads_enabled = False