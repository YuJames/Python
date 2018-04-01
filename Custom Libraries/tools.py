#!/usr/bin/env python3

"""General-purpose tools.

This module contains general-purpose tools for use in Python scripts.

Arguments:

Todo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    change debug.setter to an adder?
    name mangling
    how to document properties
    typecheck enum arg/return
    document imports versions? this module's version?
    document enum?
    ~~~~PERIODICALLY~~~~
    
"""

#~~~~  IMPORTS  ~~~~#
import datetime
import enum
import logging
import sys
import time

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#
@enum.unique
class Status(enum.Enum):
    SUCCESS = 1
    FAILURE = 0

class ResultObject():
    """Hold a function's result and error info for easy diagnostics.
    
    Attributes:
        result (any): Function's return value.
        status (Status): Function's completion status.
        message (str): Function's return message.
        debug (str): Function's debugging log.
    """
    
    _debug_start = "\n**** START DEBUG ****\n"
    _debug_end = "**** END DEBUG ****\n"
    
    def __init__(self) -> None:
        self._result = None
        self._status = None
        self._message = None
        self._debug = ""
        
    @property
    def result(self):
        print("getting result")
        return self._result
          
    @result.setter
    def result(self, result):
        print("setting result")
        self._result = result
        
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
            
    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message
        
    @property
    def debug(self):
        return ResultObject._debug_start + self._debug + ResultObject._debug_end

    @debug.setter
    def debug(self, debug):
        self._debug = self._debug + debug + "\n"

class MyLogger():
    """Context manager for logging.
    
    """
    
    def __init__(self, file):
        self._file = file
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.FileHandler(self._file))
        
    def __enter__(self):
        self._logger.info("{:%Y-%m-%d %H:%M:%S} ENTER: {}".format(datetime.datetime.now(), get_fxn_name(depth=2)))
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logger.info("{:%Y-%m-%d %H:%M:%S} EXIT: {}".format(datetime.datetime.now(), get_fxn_name(depth=2)))
    
    def write(self, level, msg):
        self._logger.log(level=level, msg=msg)
    
class MyTimer():
    """Context manager for measuring execution time.
    
    """
    
    def __init__(self):
        pass
        
    def __enter__(self):
        format_title(title=get_fxn_name(depth=2), should_print=True)
        self._start = time.time()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = time.time()
        print("function time: {} seconds".format(self._end - self._start))
        
#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def format_title(title: str, should_print=False) -> str:
    """Format a title.
    
    Args:
        title: heading (str)
    Returns:
        result: formatted title (str)
    """
    
    title_length = len(title)
    result = "\n" + title.upper() + "\n"
    for i in range(title_length):
        result += "-"
    
    if should_print is False:
        return result
    else:
        print(result)
    
def format_script_args() -> str:
    """Format script arguments.
    
    Args:
        None
    Returns:
        result: formatted script args (str)
    """
    
    result = ""
    for index, arg in enumerate(sys.argv[1:], 1):
        result += "{}: {}\n".format(index, arg)
    
    return result

def create_timestamp(output_file_path):
    """Add a formatted timestamp to a file.
    
    Args:
        output_file_path: test result file path (str)
    Returns:
        result: N/A (ResultObject)
    """
    
    result = ResultObject()
    
    try:
        with open(output_file_path, "a") as f:
            f.write("{:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.now()))
            result.set_status(1)
            result.set_message("create_timestamp: SUCCESS")            
    except Exception as e:
        result.set_status(0)
        result.set_message("create_timestamp: FAILURE")
        result.add_debug("Exception message: {}".format(repr(e)))
        
    return result

def get_fxn_name(depth=1, should_print=False):
    if should_print is True:
        print(sys._getframe(depth).f_code.co_name)
    
    return sys._getframe(depth).f_code.co_name
        
def result_handler(result_obj):
    """Handle the return of a ResultObject.
    
    Args:
        result_obj: (ResultObject)
    Returns:
        
    """
    
    None

#~~~~  MAIN  ~~~~#

#~~~~  DEAD CODE  ~~~~#