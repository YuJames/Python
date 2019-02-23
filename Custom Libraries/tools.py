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
class LoggerTimer:
    def __init__(self, file=None, timer=True):
        """Context manager for logging and measuring execution time.
        
        Args:
            file: log file (str or None)
            timer: measure execution time (bool)
        Returns:
            None
        """
        
        self._file, self._is_timer = file, timer

        if self._is_timer:
            self._start = self._end = None
            
        if self._file is not None:
            self._handler = logging.FileHandler(self._file)
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(self._handler)


    def __enter__(self):
        self.write(f"{fg_timestamp()} - [ENTER] fxn name: {g_fxn(depth=2)}")

        if self._is_timer:
            self._start = time.time()

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_timer:
            self._end = time.time()
            self.write(f"function time: {self._end - self._start} seconds")

        self.write(f"{fg_timestamp()} - [EXIT] fxn name: {g_fxn(depth=2)}")


    def write(self, msg):
        """Write to output.
        
        Args:
            msg: message to write (str)
        Returns:
            None
        """
        
        if self._file is not None:
            self._logger.info(msg)
            self._handler.flush()
        else:
            print(msg)


#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def f_title(title):
    """Format a title.
    
    Args:
        title: heading (str)
    Returns:
        formatted title (str)
    """

    return title.upper() + "\n" + ("=" * len(title)) + "\n"


def fg_args():
    """Get/format the script arguments.
    
    Args:
        N/A
    Returns:
        script args (str)
    """

    return "".join(f"{i}: {j}\n" for i, j in enumerate(sys.argv[1:], 1))


def fg_timestamp():
    """Get/format the timestamp.
    
    Args:
        N/A
    Returns:
        timestamp (str)
    """

    return f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"


def g_fxn(depth=1):
    """Get the calling function name.
    
    Args:
        depth: caller function depth in the call stack (int)
    Returns:
        caller function (str)
    """

    return sys._getframe(depth).f_code.co_name


def f_dir(obj):
    """Format public attributes of an object.
    
    Args:
        obj: object (Object)
        doc: get the documentation (bool)
    Returns:
        dicts of uncallables and callables (list)
    """
    
    both = {i: i.__doc__ for i in dir(obj) if not i.startswith("_")}
    uncallables = {i: j for i, j in both.items() if not callable(getattr(obj, i))}
    callables = {i: j for i, j in both.items() if callable(getattr(obj, i))}
    return [uncallables, callables]
    
    
#~~~~  MAIN  ~~~~#
def main():
    pass
        
if __name__ == "__main__":
    main()
    
#~~~~  DEAD CODE  ~~~~#