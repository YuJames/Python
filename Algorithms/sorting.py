#!/usr/bin/env python3

"""Sorting Algorithms.

This module provides sorting functionality.
    
ToDo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    make solution more pythonic
    ~~~~PERIODICALLY~~~~
    improve docstrings
    improve modularity (globals, fxns, variables)
    improve naming
    return vs return None vs nothing
    
"""

def bubble_sort(data):
    """Sort a list of unique numbers in ascending order using bubble sort. O(n^2).
    
    The process includes repeatedly iterating through a list and swapping adjacent elements. 
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    n = len(data)
    sorted_data = data[:]
    is_ordered = True
    
    # make up to n - 1 iterations
    for i in range(n - 1):
        # ignore the ordered, last values
        for j in range(n - 1 - i):
            # compare 2 adjacent values
            if sorted_data[j] > sorted_data[j+1]:
                sorted_data[j], sorted_data[j+1] = sorted_data[j+1], sorted_data[j]
                is_ordered = False

        # terminate early
        if is_ordered is True:
            break
        else:
            is_ordered = True
    
    return sorted_data

def quick_sort(data):
    """Sort a list of unique numbers in ascending order using quick sort. O(n^2).
    
    The process includes recursively splitting a list into a pivot, smaller side, and larger side.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    n = len(data)
    
    # terminate early
    if n < 2:
        return data
    
    pivot = data[0]

    # organize data around pivot
    left = [value for i, value in enumerate(data[1:]) if value < pivot]
    right = [value for i, value in enumerate(data[1:]) if value > pivot]
    # make recursive calls
    sorted_left = quick_sort(left)
    sorted_right = quick_sort(right)
        
    # combine sorted data with pivot
    sorted_data = sorted_left
    sorted_data.append(pivot)
    sorted_data.extend(sorted_right)
    
    return sorted_data

def insert_sort(data):
    """Sort a list of unique numbers in ascending order using insert sort. O(n^2).
    
    The process includes iterating through a list and ordering elements as they're visited.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    sorted_data = data[:]
    
    # visit new elements
    for i, value in enumerate(sorted_data):
        # compare each new element with previously visited elements
        for j in range(i, -1, -1):
            # swap if needed
            if sorted_data[j] > value:
                sorted_data[j + 1] = sorted_data[j]
                sorted_data[j] = value
    
    return sorted_data

def selection_sort(data):
    """Sort a list of unique numbers in ascending order using selection sort. O(n^2).
    
    The process includes repeatedly iterating through a list, finding the smallest element, and sorting that element.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """

    sorted_data = data[:]
    
    for i, value in enumerate(sorted_data):
        # find smallest value in unsorted subset
        min_value = min(sorted_data[i:])
        index_min = sorted_data.index(min_value)
        
        # place smallest value at start of unsorted subset
        sorted_data[i], sorted_data[index_min] = min_value, value

    return sorted_data

def merge_sort(data):
    """Sort a list of unique numbers in ascending order using merge sort. .
    
    The process includes recursively splitting a list to a smaller and larger side.
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    # split
    data_len = len(data)
    
    # terminate early
    if data_len == 1:
        return data

    # split
    left = data[:data_len // 2]
    right = data[data_len // 2:]

    # make recursive calls
    sorted_left = merge_sort(left)
    sorted_right = merge_sort(right)
    
    # combine
    sorted_data = []
    while True:
        smaller = None
        if len(sorted_left) != 0 and len(sorted_right) != 0:
            smaller = sorted_left.pop(0) if sorted_left[0] < sorted_right[0] else sorted_right.pop(0)
        elif len(sorted_left) != 0:
            smaller = sorted_left.pop(0)
        elif len(sorted_right) != 0:
            smaller = sorted_right.pop(0)
        else:
            break
            
        sorted_data.append(smaller)
    
    return sorted_data
    
def heap_sort(data):
    """Sort a list of unique numbers in ascending order using heap sort. .
    
    N/A
    
    Args:
        data: data to sort (list of int)
    Returns:
        sorted list
    """
    
    pass
    
a = [1, -1, 8, -8, 240]
b = [1, 2]
print(insert_sort(a))
