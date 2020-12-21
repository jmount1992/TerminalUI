# #!/usr/bin/env python

# ### IMPORT MODULES ### 
# import curses
# from curses.textpad import Textbox, rectangle

# import numpy as np


# class TerminalGUI():
#     """
#     docstring
#     """

#     ### INITALISE ###
#     def __init__(self, stdscr):
        
#         # CONSTANTS
#         self.WRITE_WINDOW_HEIGHT_PERCENTAGE = 0.1
#         self.WRITE_WINDOW_HEIGHT_LIMTS = [3, 5]
#         self.OPTIONS_WINDOW_WIDTH_PERCENTAGE = 0.2
#         self.OPTIONS_WINDOW_WIDTH_LIMITS = [10, 20]

#         # VARIABLES
#         self.stdscr = stdscr
#         self.windows = [None, None, None] # List of window objects [write, receive, options]
#         self.window_sizes = np.repeat(np.array([[curses.LINES, curses.COLS]]), 4, axis=0) # cols = [height, width] rows = [terminal_size, write_window_size, receive_window_size, options_window_size]

#         # INITIALISE SCREEN
#         stdscr.clear()
#         curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
#         curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
#         curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

#         # INITIALISE WINDOWS
#         self.InitialiseWindows()

#         # Testing
#         while True:
#             pass
            
#             # Dynamic Resizing
#             k = self.stdscr.getch()
#             if k == curses.KEY_RESIZE:
#                 self.stdscr.addstr(0,0,"Terminal Resize")
#                 self.UpdateWindows()
            



#     ### INITIALISE WINDOWS ###
#     def InitialiseWindows(self):
#         # Calculate Current window sizes
#         self.CalculateWindowSizes()

#         # Create window objects
#         self.windows[0] = curses.newwin(self.window_sizes[1,0], self.window_sizes[1,1], self.window_sizes[2,0], 0)
#         self.windows[1] = curses.newwin(self.window_sizes[2,0], self.window_sizes[2,1], 0, 0)
#         self.windows[2] = curses.newwin(self.window_sizes[3,0], self.window_sizes[3,1], 0, self.window_sizes[2,1])

#         # Testing
#         for idx in range(3):
#             self.windows[idx].bkgd(curses.color_pair(idx+1))
#             self.windows[idx].refresh()

    
#     def UpdateWindows(self):
#         # Calculate current window sizes
#         self.CalculateWindowSizes()

#         # Resize and move windows
#         for idx in range(3):
#             self.windows[idx].resize(self.window_sizes[idx+1,0], self.window_sizes[idx+1,1])
#             # if idx == 0: # write window
#             #     self.windows[idx].mvwin(self.window_sizes[2,0], 0)
#             # elif idx == 2: # options window
#             #     self.windows[idx].mvwin(0, self.window_sizes[2,1])
#             self.windows[idx].refresh()


#     def CalculateWindowSizes(self):
#         # Get current terminal size
#         self.window_sizes[0,:] = np.array([curses.LINES-1, curses.COLS-1])

#         # Get write, receive and options window heights - based on write window minimum
#         self.window_sizes[1,0] = np.maximum(self.WRITE_WINDOW_HEIGHT_LIMTS[0], np.ceil(self.window_sizes[1,0]*self.WRITE_WINDOW_HEIGHT_PERCENTAGE))
#         self.window_sizes[2,0] = self.window_sizes[2,0] - self.window_sizes[1,0]
#         self.window_sizes[3,0] = self.window_sizes[2,0]

#         # Get options and receive window widths - based on options window minimum
#         self.window_sizes[3,1] = np.maximum(self.OPTIONS_WINDOW_WIDTH_LIMITS[0], np.ceil(self.window_sizes[1,1]*self.OPTIONS_WINDOW_WIDTH_PERCENTAGE))
#         self.window_sizes[2,1] = self.window_sizes[2,1] - self.window_sizes[3,1]



# ### MAIN FUNCTION ###

# def main(stdscr):
#     terminal_gui = TerminalGUI(stdscr)


# if __name__ == "__main__":

#     try:
#         curses.wrapper(main)
#     except KeyboardInterrupt:
#         pass # so CTRL+C does not print to the terminal

import urwid

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    txt.set_text(repr(key))

txt = urwid.Text(u"Hello World")
fill = urwid.Filler(txt, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
loop.run()