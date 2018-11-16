#!/usr/bin/env python3

"""General-purpose tools.

This module contains general-purpose tools for use in Python scripts.

Arguments:
    N/A

Todo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    name mangling
    how to document properties
    static typecheck
    document imports versions? this module's version?
    document enum?
    ~~~~PERIODICALLY~~~~
    
"""

#~~~~  IMPORTS  ~~~~#
import datetime
import logging
import sys
import time

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#
class LoggerAndTimer:
    def __init__(self, file=None, timer=True):
        """Context manager for logging and measuring execution time.
        
        Args:
            file: log file (str or None)
            timer: measure execution time (bool)
        Returns:
            None
        """
        self._file = file
        self._track_time = timer
        self._output = ""

        if file is not None:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(logging.FileHandler(self._file))


    def __enter__(self):
        self._output += f"{fg_timestamp(False)} - [ENTER] fxn name: {g_fxn(depth=2)}\n"

        if self._track_time:
            self._start = time.time()

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._track_time:
            self._end = time.time()
            self._output += f"function time: {self._end - self._start} seconds\n"

        self._output += f"{fg_timestamp(False)} - [EXIT] fxn name: {g_fxn(depth=2)}\n"

        if self._file is not None:
            self._logger.info(self._output)
        else:
            print(self._output)


    def write(self, msg, cr=True):
        """Add to the output message.
        
        Args:
            msg: message to add (str)
            cr: carriage return at end (bool)
        Returns:
            None
        """
        
        self._output += (msg + ("\n" if cr else ""))


#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def f_title(title, cr=True):
    """Format a title.
    
    Args:
        title: heading (str)
        cr: carriage return at end (bool)
    Returns:
        formatted title (str)
    """

    return title.upper() + "\n" + ("=" * len(title)) + ("\n" if cr else "")


def fg_args(cr=True):
    """Get/format the script arguments.
    
    Args:
        N/A
    Returns:
        script args (str)
    """

    args = "".join([f"{i}: {j}\n" for i, j in enumerate(sys.argv[1:], 1)])
    
    if cr:
        return args
    else:
        return args[:-1]


def fg_timestamp(cr=True):
    """Get/format the timestamp.
    
    Args:
        cr: carriage return at end (bool)
    Returns:
        timestamp (str)
    """

    return f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}" + ("\n" if cr else "")


def g_fxn(depth=1):
    """Get the calling function name.
    
    Args:
        depth: caller function depth in the call stack (int)
    Returns:
        caller function (str)
    """

    return sys._getframe(depth).f_code.co_name


#~~~~  MAIN  ~~~~#
def test():
    with LoggerAndTimer() as f:
        f.write("hi")
        
if __name__ == "__main__":
    test()
#~~~~  DEAD CODE  ~~~~#