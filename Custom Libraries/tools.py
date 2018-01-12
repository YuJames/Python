"""General-purpose tools.

This module contains general-purpose tools for use in Python scripts.
    
Todo:
    check if need to inherit from 'object' class to use @property
    change debug.setter to an adder?
    name mangling
    how to document properties
    typecheck enum arg/return
    document imports versions? this module's version?
    document enum?
    
"""

#~~~~  imports  ~~~~#
import datetime
import enum
import sys

#~~~~  global variables  ~~~~#


#~~~~  classes  ~~~~#
@enum.unique
class Status(enum.Enum):
    SUCCESS = 1
    FAILURE = 0

class ResultObject(object):
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
        
#~~~~  functions  ~~~~#
def make_formatted_title(title: str) -> str:
    """Format a title.
    
    Args:
        title: heading (string)
    Returns:
        result: formatted title (string)
    """
    
    title_length = len(title)
    result = "\n" + title.upper() + "\n"
    for i in range(title_length):
        result += "-"

    return result
    
def make_formatted_script_args() -> str:
    """Format script arguments.
    
    Args:
        None
    Returns:
        result: formatted script args (string)
    """
    
    result = ""
    for index, arg in enumerate(sys.argv[1:], 1):
        result += "{}: {}\n".format(index, arg)
    
    return result

def create_timestamp(output_file_path):
    """Add a formatted timestamp to a file.
    
    Args:
        output_file_path: test result file path (string)
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

def print_fxn_name(depth=1):
    print(sys._getframe(1).f_code.co_name)
    
def result_handler(result_obj):
    """Handle the return of a ResultObject.
    
    Args:
        result_obj: (ResultObject)
    Returns:
        
    """
    
    None
