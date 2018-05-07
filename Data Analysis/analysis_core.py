#!/usr/bin/env python3

"""Core Resources.

This module provides common resources for the different analysis types in data_analysis.py.

ToDo:
    ~~~~NOW~~~~
    replace _JsonKey precision 
    ~~~~CONSIDERATION~~~~
    ~~~~PERIODICALLY~~~~
"""

#~~~~  IMPORTS  ~~~~#
import numpy as np
import pandas as pd
import typing

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#
class AnalysisData():
    def __init__(self):
        self._sources = {}
        self._data = {}
        
class AnalysisFigure():
    def __init__(self):
        self._data = None
        self._figure = None
        self._annotations = {}
        self._widgets = {}
        
#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def is_string_number(data: str) -> bool:
    """Check if string contents represent a number.
    
    Args:
        data: data to analyze (str)
    Returns:
        result of check (bool)
    """
    
    # terminate early
    if data == "":
        return False
    
    try:
        float(data)
    except ValueError:
        return False
    else:
        return True
        
def calc_avg(data: pd.Series, prec=None) -> float:
    """Calculate average.
    
    Args:
        data: data to analyze (pd.Series)
        prec: precision if rounding (int)
    Returns:
        average (float)
    """
    
    average = data.mean(axis=0)
    if prec is not None:
        average = round(number=average, ndigits=prec)

    return average
    
def calc_avg_moving_range(data: pd.Series, length: int, prec=None) -> float:
    """Calculate average mR.
    
    Args:
        data: data to analyze (pd.Series)
        length: length of data subsets (int)
        prec: precision if rounding (int)
    Returns:
        average mR (float)
    """
    
    count = 0.0
    # data subsets to calculate mR on
    element_pairs = zip(data[:-(length - 1)], data[(length - 1):])
    # calculations
    for (left, right) in element_pairs:
        count += abs(left - right)
        
    result = count / (len(data) - (length - 1))
    if prec is not None:
        result = round(number=result, ndigits=prec)
    
    return result
    
def calc_var_limits(data: pd.Series, prec=None) -> typing.Tuple[float, float]:
    """Calculate upper/lower range limits.
    
    Args:
        data: data to analyze (pd.Series)
        prec: precision if rounding (int)
    Returns:
        (upper, lower) (float 2-tuple)
    """
    
    # calculate averages
    average = calc_avg(data=data, prec=prec)
    average_moving_range = calc_avg_moving_range(data=data, length=2, prec=prec)
    
    # calculate limits
    upper_natural_process_limits = average + (2.66 * average_moving_range)
    lower_natural_process_limits = average - (2.66 * average_moving_range)
    
    result = (lower_natural_process_limits, upper_natural_process_limits)
    if prec is not None:
        result = (round(number=result[0], ndigits=prec), 
                  round(number=result[1], ndigits=prec))
    
    return result
    
def calc_cpk(data: pd.Series, lower: float, upper: float, prec=None) -> float:
    """Calculate cpk (capability statistics).
    
    Args:
        data: data to analyze (pd.Series)
        lower: lower limit (float)
        upper: upper limit (float)
        prec: precision if rounding (int)
    Returns:
        cpk (float)
    """

    arr = np.array(object=[x for x in data]).ravel()
    sigma = np.std(a=arr)
    mean = np.mean(a=data)
    
    left = np.float64(upper - mean) / (3 * sigma)
    right = np.float64(mean - lower) / (3 * sigma)
    
    result = min(left, right)
    if prec is not None:
        result = round(number=result, ndigits=prec)
    
    return result

def calc_failures(data: pd.Series, lower: float, upper: float, prec=None) -> typing.Tuple[float, float]:
    """Calculate failures.
    
    Args:
        data: data to analyze (pd.Series)
        lower: lower limit (float)
        upper: upper limit (float)    
        prec: precision if rounding (int)   
    Returns:
        (number, percent) (float 2-tuple)
    """
    
    length = data.shape[0]
    count = 0.0
    for x in data:
        if x < lower or x > upper:
            count += 1
            
    result = (count, count * 100 / length)
    if prec is not None:
        result = (result[0], round(number=result[1], ndigits=prec))

    return result

#~~~~  MAIN  ~~~~#

#~~~~  DEAD CODE  ~~~~#
