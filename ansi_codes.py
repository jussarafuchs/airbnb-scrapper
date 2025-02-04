import os
import sys
import ctypes

def enable_ansi_escape_codes():
    if os.name == 'nt':  # Check if the OS is Windows
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # Get the handle for the console
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # Enable Virtual Terminal Processing

